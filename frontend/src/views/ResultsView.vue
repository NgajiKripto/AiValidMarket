<template>
  <div class="results-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
      </div>
    </nav>

    <main class="content" v-if="result">
      <section class="summary-section">
        <h1 class="page-title">Validation Results</h1>
        <div class="score-card">
          <span class="score-value" :class="scoreClass">{{ result.market_viability_score || '?' }}</span>
          <span class="score-label">/ 10 Market Viability</span>
        </div>
        <p class="executive-summary">{{ result.executive_summary }}</p>
      </section>

      <section class="section" v-if="result.keywords_analysis">
        <h2 class="section-title">Keywords</h2>
        <div class="keywords-grid">
          <span
            v-for="(kw, i) in keywordsList"
            :key="i"
            class="keyword-tag"
            @click="copyKeyword(kw)"
          >{{ kw }}</span>
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
        <div class="sources-grid">
          <div v-for="(source, i) in sourcesList" :key="i" class="source-card">
            <span class="source-type">{{ source.source_type || 'web' }}</span>
            <a :href="source.link" target="_blank" rel="noopener" class="source-title">
              {{ source.title }}
            </a>
            <p class="source-snippet" v-if="source.snippet">{{ source.snippet }}</p>
          </div>
        </div>
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

    <main class="content" v-else>
      <p class="loading-text">Loading results...</p>
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
  background: #000;
  color: #fff;
  padding: 16px 24px;
  border-bottom: 3px solid #000;
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
  letter-spacing: 2px;
  color: #fff;
}

.content {
  max-width: 900px;
  margin: 0 auto;
  padding: 48px 24px;
  width: 100%;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 24px;
}

.score-card {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
  padding: 24px;
  border: 3px solid #000;
}

.score-value {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1;
}

.score-high { color: #22c55e; }
.score-mid { color: #FF4500; }
.score-low { color: #ef4444; }

.score-label {
  font-size: 1rem;
  color: #444;
}

.executive-summary {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #222;
  margin-bottom: 32px;
}

.section {
  margin-bottom: 40px;
  border-top: 3px solid #000;
  padding-top: 24px;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
}

.keywords-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  padding: 8px 14px;
  border: 2px solid #000;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.keyword-tag:hover {
  background: #000;
  color: #fff;
}

.questions-list {
  list-style: none;
}

.question-item {
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.9rem;
}

.question-item::before {
  content: '?';
  font-weight: 700;
  color: #FF4500;
  margin-right: 8px;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.source-card {
  border: 2px solid #000;
  padding: 16px;
}

.source-type {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #FF4500;
  display: block;
  margin-bottom: 8px;
}

.source-title {
  font-size: 0.9rem;
  font-weight: 600;
  display: block;
  margin-bottom: 6px;
  text-decoration: underline;
}

.source-title:hover {
  color: #FF4500;
}

.source-snippet {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.5;
}

.chat-section {
  margin-top: 48px;
}

.chat-messages {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
  border: 2px solid #e0e0e0;
  padding: 16px;
}

.chat-msg {
  margin-bottom: 12px;
}

.chat-msg.user .msg-role {
  color: #000;
  font-weight: 700;
}

.chat-msg.assistant .msg-role {
  color: #FF4500;
  font-weight: 700;
}

.msg-role {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 4px;
}

.msg-text {
  font-size: 0.9rem;
  line-height: 1.6;
}

.chat-input-wrap {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 14px;
  border: 3px solid #000;
  font-size: 0.9rem;
  outline: none;
}

.chat-input:focus {
  border-color: #FF4500;
}

.chat-btn {
  padding: 14px 24px;
  background: #000;
  color: #fff;
  border: 3px solid #000;
  font-weight: 700;
  text-transform: uppercase;
  transition: all 0.2s;
}

.chat-btn:hover:not(:disabled) {
  background: #FF4500;
  border-color: #FF4500;
}

.chat-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-text {
  color: #FF4500;
  font-size: 0.95rem;
  margin-bottom: 16px;
}

.back-link {
  border: 2px solid #000;
  padding: 12px 24px;
  display: inline-block;
  font-weight: 600;
}

.back-link:hover {
  background: #000;
  color: #fff;
}

.loading-text {
  font-size: 1rem;
  color: #444;
}
</style>
