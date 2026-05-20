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
        <textarea
          v-model="ideaText"
          class="idea-input"
          placeholder="Describe your startup idea here... Be as detailed as possible about what you want to build, who it's for, and what problem it solves."
          rows="6"
        ></textarea>
        <button
          class="validate-btn"
          :disabled="!ideaText.trim() || isSubmitting"
          @click="handleSubmit"
        >
          {{ isSubmitting ? 'Submitting...' : 'Validate Idea' }}
        </button>
        <p v-if="error" class="error-text">{{ error }}</p>
      </section>

      <section class="workflow">
        <h2 class="workflow-title">How it works</h2>
        <div class="steps">
          <div class="step">
            <span class="step-number">01</span>
            <h3 class="step-label">AI Analysis</h3>
            <p class="step-desc">Our AI breaks down your idea into key components, identifying target markets and potential keywords.</p>
          </div>
          <div class="step">
            <span class="step-number">02</span>
            <h3 class="step-label">Market Research</h3>
            <p class="step-desc">Automated web research gathers real data about competitors, demand signals, and market trends.</p>
          </div>
          <div class="step">
            <span class="step-number">03</span>
            <h3 class="step-label">Validation Report</h3>
            <p class="step-desc">Get a comprehensive report with viability scores, keywords, questions, and actionable recommendations.</p>
          </div>
        </div>
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
  background: #000;
  color: #fff;
  padding: 16px 24px;
  border-bottom: 3px solid #000;
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
  letter-spacing: 2px;
}

.nav-link {
  color: #fff;
  font-size: 0.85rem;
  border: 1px solid #fff;
  padding: 6px 12px;
  transition: all 0.2s;
}

.nav-link:hover {
  background: #FF4500;
  border-color: #FF4500;
}

.content {
  max-width: 800px;
  margin: 0 auto;
  padding: 60px 24px;
  flex: 1;
  width: 100%;
}

.hero {
  text-align: center;
  margin-bottom: 48px;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -1px;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 1rem;
  color: #444;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.7;
}

.input-section {
  margin-bottom: 64px;
}

.idea-input {
  width: 100%;
  padding: 20px;
  border: 3px solid #000;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 160px;
  outline: none;
  transition: border-color 0.2s;
}

.idea-input:focus {
  border-color: #FF4500;
}

.validate-btn {
  display: block;
  width: 100%;
  margin-top: 16px;
  padding: 18px 32px;
  background: #000;
  color: #fff;
  border: 3px solid #000;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: all 0.2s;
}

.validate-btn:hover:not(:disabled) {
  background: #FF4500;
  border-color: #FF4500;
}

.validate-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-text {
  color: #FF4500;
  margin-top: 12px;
  font-size: 0.85rem;
}

.workflow {
  border-top: 3px solid #000;
  padding-top: 48px;
}

.workflow-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 32px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
}

.step {
  border: 3px solid #000;
  padding: 24px;
}

.step-number {
  font-size: 2rem;
  font-weight: 700;
  color: #FF4500;
  display: block;
  margin-bottom: 12px;
}

.step-label {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.step-desc {
  font-size: 0.85rem;
  color: #444;
  line-height: 1.6;
}
</style>
