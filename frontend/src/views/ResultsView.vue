<template>
  <div class="results-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
        <div class="nav-links">
          <router-link to="/memory" class="nav-link">Memory</router-link>
        </div>
      </div>
    </nav>

    <main class="content" v-if="result">
      <section class="summary-section">
        <h1 class="page-title">Validation Results</h1>
        <div class="score-row">
          <span class="score-text" :class="scoreClass">
            Score: <span class="score-num">{{ result.market_viability_score || '?' }}</span> / 10
          </span>
          <span class="score-label">Market Viability</span>
          <div class="score-bar">
            <div
              class="score-bar-fill"
              :class="scoreClass"
              :style="{ width: ((result.market_viability_score || 0) / 10 * 100) + '%' }"
            ></div>
          </div>
        </div>
        <p class="executive-summary">{{ result.executive_summary }}</p>
      </section>

      <section class="section" v-if="result.keywords_analysis">
        <h2 class="section-title">Keywords</h2>
        <div class="keywords-wrap">
          <button
            v-for="(kw, i) in keywordsList"
            :key="i"
            class="keyword-pill"
            :class="{ copied: copiedKeyword === kw }"
            @click="copyKeyword(kw)"
            type="button"
            title="Click to copy"
          >{{ copiedKeyword === kw ? 'Copied!' : kw }}</button>
        </div>
      </section>

      <section class="section" v-if="result.questions_analysis">
        <h2 class="section-title">Questions People Ask</h2>
        <ul class="questions-list">
          <li v-for="(q, i) in questionsList" :key="i" class="question-item">{{ q }}</li>
        </ul>
      </section>

      <section class="section" v-if="result.sources">
        <h2 class="section-title">Sources</h2>
        <ul class="sources-list">
          <li v-for="(source, i) in sourcesList" :key="i" class="source-item">
            <span class="source-type-badge">{{ source.source_type || 'web' }}</span>
            <a :href="source.link" target="_blank" rel="noopener" class="source-link">
              {{ source.title }}
            </a>
            <p class="source-snippet" v-if="source.snippet">{{ source.snippet }}</p>
          </li>
        </ul>
      </section>

      <section class="section chat-section">
        <h2 class="section-title">Ask Follow-up Questions</h2>
        <div class="chat-messages" ref="chatContainer">
          <div
            v-for="(msg, i) in chatHistory"
            :key="i"
            class="chat-msg"
            :class="msg.role"
          >
            <span class="msg-role">{{ msg.role === 'user' ? 'You' : 'AI' }}</span>
            <p class="msg-text">{{ msg.content }}</p>
          </div>
        </div>
        <div class="chat-input-wrap">
          <input
            v-model="chatInput"
            class="chat-input"
            placeholder="Ask a follow-up question..."
            aria-label="Ask a follow-up question"
            @keyup.enter="sendChat"
          />
          <button class="chat-btn" :disabled="!chatInput.trim() || isChatting" @click="sendChat">
            Send
          </button>
        </div>
      </section>
    </main>

    <main class="content" v-else-if="error">
      <p class="error-text">{{ error }}</p>
      <router-link to="/" class="back-link">Back to Home</router-link>
    </main>

    <main class="content loading-state" v-else>
      <div class="skeleton-block skeleton-title"></div>
      <div class="skeleton-block skeleton-body"></div>
      <div class="skeleton-block skeleton-body short"></div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getValidationResult, chatWithAgent } from '@/api/validation'

const route = useRoute()
const taskId = route.params.taskId

const result = ref(null)
const error = ref('')
const chatHistory = ref([])
const chatInput = ref('')
const isChatting = ref(false)
const chatContainer = ref(null)
const copiedKeyword = ref(null)

const scoreClass = computed(() => {
  const score = result.value?.market_viability_score || 0
  if (score >= 7) return 'score-high'
  if (score >= 4) return 'score-mid'
  return 'score-low'
})

const keywordsList = computed(() => {
  const ka = result.value?.keywords_analysis
  if (Array.isArray(ka)) return ka
  if (typeof ka === 'string') return ka.split(',').map(k => k.trim())
  if (ka?.keywords) return ka.keywords
  return []
})

const questionsList = computed(() => {
  const qa = result.value?.questions_analysis
  if (Array.isArray(qa)) return qa
  if (qa?.questions) return qa.questions
  return []
})

const sourcesList = computed(() => {
  const s = result.value?.sources
  if (!s) return []
  if (Array.isArray(s)) return s
  const all = []
  if (s.websites) all.push(...s.websites.map(x => ({ ...x, source_type: 'website' })))
  if (s.social_media) all.push(...s.social_media.map(x => ({ ...x, source_type: 'social' })))
  if (s.geographic) all.push(...s.geographic.map(x => ({ ...x, source_type: 'geographic' })))
  return all
})

function copyKeyword(kw) {
  navigator.clipboard?.writeText(kw)
  copiedKeyword.value = kw
  setTimeout(() => {
    if (copiedKeyword.value === kw) {
      copiedKeyword.value = null
    }
  }, 1500)
}

async function sendChat() {
  if (!chatInput.value.trim() || isChatting.value) return
  const message = chatInput.value.trim()
  chatHistory.value.push({ role: 'user', content: message })
  chatInput.value = ''
  isChatting.value = true

  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }

  try {
    const response = await chatWithAgent(taskId, message, chatHistory.value)
    chatHistory.value.push({ role: 'assistant', content: response.data.response })
  } catch (err) {
    chatHistory.value.push({ role: 'assistant', content: 'Sorry, failed to get a response.' })
  } finally {
    isChatting.value = false
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }
}

onMounted(async () => {
  try {
    const response = await getValidationResult(taskId)
    const data = response.data.result || response.data
    result.value = data.report || data
  } catch (err) {
    error.value = 'Failed to load results. The validation may still be in progress.'
  }
})
</script>

<style scoped>
.results-view {
  min-height: 100vh;
}

.navbar {
  background: var(--color-navbar-bg);
  color: var(--color-text-on-accent);
  padding: var(--space-4) var(--space-6);
}

.navbar-inner {
  max-width: var(--page-width);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-weight: 700;
  font-size: var(--text-lg);
  letter-spacing: 0.08em;
  color: var(--color-text-on-accent);
}

.brand:focus-visible {
  box-shadow: 0 0 0 2px var(--color-navbar-bg), 0 0 0 4px var(--color-accent);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.nav-link {
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  border: 1px solid oklch(0.7 0.01 170);
  border-radius: var(--radius-sm);
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  color: var(--color-text-on-accent);
}

.nav-link:hover {
  background: oklch(0.3 0.01 170);
  border-color: oklch(0.5 0.01 170);
}

.nav-link:focus-visible {
  box-shadow: 0 0 0 2px var(--color-navbar-bg), 0 0 0 4px var(--color-accent);
}

.content {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
  width: 100%;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-6);
  text-wrap: balance;
  line-height: var(--leading-tight);
  color: var(--color-text);
}

/* Score display - inline bar, NOT hero-metric */
.score-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.score-text {
  font-size: var(--text-lg);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.score-num {
  font-weight: 700;
}

.score-high { color: var(--color-success); }
.score-mid { color: var(--color-warning); }
.score-low { color: var(--color-error); }

.score-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.score-bar {
  width: 100%;
  height: 6px;
  background: var(--color-border-muted);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-slow) var(--ease);
}

.score-bar-fill.score-high { background: var(--color-success); }
.score-bar-fill.score-mid { background: var(--color-warning); }
.score-bar-fill.score-low { background: var(--color-error); }

.executive-summary {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
  max-width: 65ch;
}

.section {
  margin-bottom: var(--space-12);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-4);
  color: var(--color-text);
}

/* Keywords - inline pills */
.keywords-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.keyword-pill {
  padding: var(--space-2) var(--space-3);
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border: 1px solid var(--color-accent-muted);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  transition: background var(--duration-fast) var(--ease),
              color var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease);
}

.keyword-pill:hover {
  background: var(--color-accent);
  color: var(--color-text-on-accent);
  border-color: var(--color-accent);
}

.keyword-pill:active {
  background: var(--color-accent-active);
  border-color: var(--color-accent-active);
}

.keyword-pill:focus-visible {
  box-shadow: var(--focus-ring);
}

.keyword-pill.copied {
  background: var(--color-accent);
  color: var(--color-text-on-accent);
  border-color: var(--color-accent);
}

/* Questions - clean list */
.questions-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.question-item {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border-muted);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}

.question-item:last-child {
  border-bottom: none;
}

/* Sources - varied list, NOT identical card grid */
.sources-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.source-item {
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease);
}

.source-item:hover {
  background: var(--color-accent-subtle);
}

.source-type-badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
  background: var(--color-accent-subtle);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-2);
}

.source-link {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  display: block;
  margin-bottom: var(--space-1);
  text-decoration: underline;
  text-decoration-color: var(--color-border);
  text-underline-offset: 2px;
  transition: color var(--duration-fast) var(--ease),
              text-decoration-color var(--duration-fast) var(--ease);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.source-link:hover {
  color: var(--color-accent);
  text-decoration-color: var(--color-accent);
}

.source-link:focus-visible {
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-sm);
}

.source-snippet {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  line-height: var(--leading-normal);
  max-width: 55ch;
}

/* Chat section */
.chat-section {
  margin-top: var(--space-12);
}

.chat-messages {
  max-height: 320px;
  overflow-y: auto;
  margin-bottom: var(--space-4);
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.chat-msg {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  max-width: 80%;
}

.chat-msg.user {
  background: var(--color-accent-subtle);
  align-self: flex-end;
}

.chat-msg.assistant {
  background: var(--color-surface-raised);
  align-self: flex-start;
}

.msg-role {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  display: block;
  margin-bottom: var(--space-1);
  color: var(--color-text-muted);
}

.chat-msg.user .msg-role {
  color: var(--color-accent);
}

.msg-text {
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--color-text);
}

.chat-input-wrap {
  display: flex;
  gap: var(--space-2);
}

.chat-input {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  min-height: 44px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  outline: none;
  background: var(--color-surface-raised);
  color: var(--color-text);
  transition: border-color var(--duration-fast) var(--ease),
              box-shadow var(--duration-fast) var(--ease);
}

.chat-input:hover {
  border-color: #99c2bc;
  border-color: oklch(0.75 0.03 170);
}

.chat-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12);
  box-shadow: 0 0 0 3px oklch(0.55 0.14 170 / 0.12);
}

.chat-btn {
  padding: var(--space-3) var(--space-6);
  min-height: 44px;
  background: var(--color-accent);
  color: var(--color-text-on-accent);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease);
}

.chat-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.chat-btn:active:not(:disabled) {
  background: var(--color-accent-active);
  border-color: var(--color-accent-active);
}

.chat-btn:focus-visible {
  box-shadow: var(--focus-ring);
}

.chat-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-text {
  color: var(--color-error);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--color-error-bg);
  border-radius: var(--radius-sm);
}

.back-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: var(--space-3) var(--space-6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease);
}

.back-link:hover {
  background: var(--color-surface);
  border-color: var(--color-accent);
}

.back-link:focus-visible {
  box-shadow: var(--focus-ring);
}

/* Loading skeleton state */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--color-surface) 0%,
    var(--color-border-muted) 50%,
    var(--color-surface) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

.skeleton-title {
  height: 32px;
  width: 60%;
}

.skeleton-body {
  height: 16px;
  width: 100%;
}

.skeleton-body.short {
  width: 40%;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 600px) {
  .content {
    padding: var(--space-8) var(--space-4);
  }

  .chat-msg {
    max-width: 90%;
  }

  .score-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
