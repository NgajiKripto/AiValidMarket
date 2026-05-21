<template>
  <div class="validation-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
        <div class="nav-links">
          <router-link to="/memory" class="nav-link">Memory</router-link>
        </div>
      </div>
    </nav>

    <main class="content">
      <h1 class="title">Validating Your Idea</h1>
      <p class="subtitle">Please wait while we analyze and research your concept.</p>

      <div class="steps">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step"
          :class="{ active: currentStep === index, completed: currentStep > index }"
        >
          <div class="step-indicator">
            <span v-if="currentStep > index" class="check-icon">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <path d="M4 9.5L7.5 13L14 5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span v-else-if="currentStep === index" class="pulse-dot"></span>
            <span v-else class="step-num">{{ index + 1 }}</span>
          </div>
          <div class="step-info">
            <h3 class="step-label">{{ step.label }}</h3>
            <p class="step-desc">{{ step.description }}</p>
            <div v-if="currentStep === index" class="skeleton-bar"></div>
          </div>
        </div>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getValidationStatus } from '@/api/validation'

const route = useRoute()
const router = useRouter()

const taskId = route.params.taskId
const currentStep = ref(0)
const error = ref('')
let pollInterval = null

const steps = [
  { label: 'Analyzing Idea', description: 'AI is breaking down your concept into key components.' },
  { label: 'Researching Market', description: 'Searching the web for market data, competitors, and trends.' },
  { label: 'Generating Report', description: 'Synthesizing all findings into a validation report.' }
]

function mapStatusToStep(status, message) {
  if (status === 'completed') return 3
  if (status === 'failed') return -1
  if (message) {
    if (message.includes('report') || message.includes('generat')) return 2
    if (message.includes('research') || message.includes('search')) return 1
  }
  return 0
}

async function pollStatus() {
  try {
    const response = await getValidationStatus(taskId)
    const data = response.data

    if (data.status === 'completed') {
      currentStep.value = 3
      clearInterval(pollInterval)
      setTimeout(() => {
        router.push(`/results/${taskId}`)
      }, 1000)
      return
    }

    if (data.status === 'failed') {
      clearInterval(pollInterval)
      error.value = data.error || 'Validation failed. Please try again.'
      return
    }

    currentStep.value = mapStatusToStep(data.status, data.message)
  } catch (err) {
    error.value = 'Failed to check status. Please refresh the page.'
    clearInterval(pollInterval)
  }
}

onMounted(() => {
  pollStatus()
  pollInterval = setInterval(pollStatus, 2000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.validation-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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
  max-width: 600px;
  margin: 0 auto;
  padding: var(--space-16) var(--space-6);
  width: 100%;
}

.title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  text-wrap: balance;
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-12);
}

.steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.step {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-6);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  transition: background var(--duration-normal) var(--ease),
              box-shadow var(--duration-normal) var(--ease);
}

.step.active {
  background: var(--color-accent-subtle);
  box-shadow: var(--shadow-md);
}

.step.completed {
  background: var(--color-surface);
  opacity: 0.8;
}

.step-indicator {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-weight: 700;
  font-size: var(--text-sm);
  flex-shrink: 0;
  background: var(--color-border-muted);
  color: var(--color-text-muted);
  transition: background var(--duration-normal) var(--ease),
              color var(--duration-normal) var(--ease);
}

.step.active .step-indicator {
  background: var(--color-accent);
  color: var(--color-text-on-accent);
}

.step.completed .step-indicator {
  background: var(--color-success);
  color: var(--color-text-on-accent);
}

.check-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--color-text-on-accent);
  animation: pulse-dot 1.2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.skeleton-bar {
  margin-top: var(--space-3);
  height: 4px;
  border-radius: var(--radius-full);
  background: linear-gradient(
    90deg,
    var(--color-accent-muted) 0%,
    var(--color-accent-subtle) 50%,
    var(--color-accent-muted) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.step-num {
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}

.step-info {
  flex: 1;
}

.step-label {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: var(--space-1);
  color: var(--color-text);
}

.step-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}

.error-text {
  color: var(--color-error);
  margin-top: var(--space-6);
  font-size: var(--text-sm);
  padding: var(--space-3) var(--space-4);
  background: var(--color-error-bg);
  border-radius: var(--radius-sm);
}

@media (max-width: 600px) {
  .content {
    padding: var(--space-8) var(--space-4);
  }

  .step {
    padding: var(--space-4);
  }
}
</style>
