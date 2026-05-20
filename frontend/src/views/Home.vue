<template>
  <div class="home">
    <nav class="navbar">
      <div class="navbar-inner">
        <span class="brand">AIVALIDMARKET</span>
        <a
          href="https://github.com/NgajiKripto/AiValidMarket"
          target="_blank"
          rel="noopener noreferrer"
          class="nav-link"
        >
          GitHub
        </a>
      </div>
    </nav>

    <main class="content">
      <section class="hero">
        <h1 class="hero-title">Validate Your Idea</h1>
        <p class="hero-subtitle">
          AI-powered market validation. Get real-time research, keyword analysis,
          and viability scores for your startup concept.
        </p>
      </section>

      <section class="input-section">
        <label class="input-label" for="idea-textarea">Describe your idea</label>
        <textarea
          id="idea-textarea"
          v-model="ideaText"
          class="idea-input"
          placeholder="Describe your startup idea here... Be as detailed as possible about what you want to build, who it's for, and what problem it solves."
          rows="6"
          maxlength="5000"
        ></textarea>
        <span class="char-count" :class="{ 'near-limit': ideaText.length > 4500 }">
          {{ ideaText.length }} / 5000
        </span>
        <button
          class="validate-btn"
          :disabled="!ideaText.trim() || isSubmitting"
          @click="handleSubmit"
        >
          <span v-if="isSubmitting" class="btn-loading-indicator"></span>
          {{ isSubmitting ? 'Submitting...' : 'Validate Idea' }}
        </button>
        <p v-if="error" class="error-text">{{ error }}</p>
      </section>

      <section class="workflow">
        <h2 class="workflow-title">How it works</h2>
        <ol class="steps-timeline">
          <li class="timeline-item">
            <span class="timeline-number">01</span>
            <div class="timeline-content">
              <h3 class="timeline-label">AI Analysis</h3>
              <p class="timeline-desc">Our AI breaks down your idea into key components, identifying target markets and potential keywords.</p>
            </div>
          </li>
          <li class="timeline-item">
            <span class="timeline-number">02</span>
            <div class="timeline-content">
              <h3 class="timeline-label">Market Research</h3>
              <p class="timeline-desc">Automated web research gathers real data about competitors, demand signals, and market trends.</p>
            </div>
          </li>
          <li class="timeline-item">
            <span class="timeline-number">03</span>
            <div class="timeline-content">
              <h3 class="timeline-label">Validation Report</h3>
              <p class="timeline-desc">Get a comprehensive report with viability scores, keywords, questions, and actionable recommendations.</p>
            </div>
          </li>
        </ol>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { submitIdea } from '@/api/validation'

const router = useRouter()
const ideaText = ref('')
const isSubmitting = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!ideaText.value.trim()) return

  isSubmitting.value = true
  error.value = ''

  try {
    const response = await submitIdea(ideaText.value)
    const taskId = response.data.task_id
    router.push(`/validate/${taskId}`)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to submit idea. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: oklch(0.22 0.01 170);
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
}

.nav-link:hover {
  background: oklch(0.3 0.01 170);
  border-color: oklch(0.5 0.01 170);
}

.nav-link:focus-visible {
  box-shadow: 0 0 0 2px oklch(0.22 0.01 170), 0 0 0 4px var(--color-accent);
}

.content {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-16) var(--space-6);
  flex: 1;
  width: 100%;
}

.hero {
  text-align: center;
  margin-bottom: var(--space-12);
}

.hero-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: var(--space-4);
  text-wrap: balance;
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.hero-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  max-width: 60ch;
  margin: 0 auto;
  line-height: var(--leading-relaxed);
}

.input-section {
  margin-bottom: var(--space-16);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.input-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.idea-input {
  width: 100%;
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  resize: vertical;
  min-height: 160px;
  outline: none;
  background: var(--color-surface-raised);
  color: var(--color-text);
  line-height: var(--leading-normal);
  transition: border-color var(--duration-fast) var(--ease),
              box-shadow var(--duration-fast) var(--ease);
}

.idea-input:hover {
  border-color: oklch(0.75 0.03 170);
}

.idea-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px oklch(0.55 0.14 170 / 0.12);
}

.idea-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.char-count {
  align-self: flex-end;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

.char-count.near-limit {
  color: var(--color-error);
  font-weight: 600;
}

.validate-btn {
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-8);
  min-height: 44px;
  background: var(--color-accent);
  color: var(--color-text-on-accent);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease),
              transform var(--duration-fast) var(--ease);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.validate-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.validate-btn:active:not(:disabled) {
  background: var(--color-accent-active);
  border-color: var(--color-accent-active);
  transform: scale(0.98);
}

.validate-btn:focus-visible {
  box-shadow: var(--focus-ring);
}

.validate-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-loading-indicator {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: oklch(0.98 0.005 170 / 0.4);
  animation: pulse-loading 1s ease-in-out infinite;
}

@keyframes pulse-loading {
  0%, 100% { opacity: 0.4; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.error-text {
  color: var(--color-error);
  font-size: var(--text-sm);
  padding: var(--space-3);
  background: var(--color-error-bg);
  border-radius: var(--radius-sm);
}

.workflow {
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-12);
}

.workflow-title {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: var(--space-8);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text);
}

.steps-timeline {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-6);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  transition: background var(--duration-fast) var(--ease);
}

.timeline-item:nth-child(1) {
  border-inline-start: none;
  background: var(--color-accent-subtle);
}

.timeline-item:nth-child(2) {
  background: var(--color-surface);
}

.timeline-item:nth-child(3) {
  background: oklch(0.96 0.008 170);
}

.timeline-number {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
  min-width: 48px;
  line-height: var(--leading-tight);
}

.timeline-content {
  flex: 1;
}

.timeline-label {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: var(--space-1);
  color: var(--color-text);
}

.timeline-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  max-width: 55ch;
}

@media (max-width: 600px) {
  .content {
    padding: var(--space-8) var(--space-4);
  }

  .hero-title {
    font-size: var(--text-2xl);
  }

  .timeline-item {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>
