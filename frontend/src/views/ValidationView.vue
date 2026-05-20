<template>
  <div class="validation-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
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
            <span v-if="currentStep > index" class="check">&#10003;</span>
            <span v-else-if="currentStep === index" class="spinner"></span>
            <span v-else class="step-num">{{ index + 1 }}</span>
          </div>
          <div class="step-info">
            <h3 class="step-label">{{ step.label }}</h3>
            <p class="step-desc">{{ step.description }}</p>
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

function mapStatusToStep(status, progress) {
  if (status === 'completed') return 3
  if (status === 'failed') return -1
  if (progress) {
    if (progress.includes('report') || progress.includes('generat')) return 2
    if (progress.includes('research') || progress.includes('search')) return 1
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

    currentStep.value = mapStatusToStep(data.status, data.progress)
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
  max-width: 600px;
  margin: 0 auto;
  padding: 60px 24px;
  width: 100%;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 0.9rem;
  color: #444;
  margin-bottom: 48px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border: 3px solid #e0e0e0;
  transition: all 0.3s;
}

.step.active {
  border-color: #FF4500;
}

.step.completed {
  border-color: #000;
  background: #f9f9f9;
}

.step-indicator {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #000;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.step.active .step-indicator {
  border-color: #FF4500;
  color: #FF4500;
}

.step.completed .step-indicator {
  background: #000;
  color: #fff;
}

.check {
  font-size: 1.2rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #FF4500;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.step-num {
  font-size: 1rem;
}

.step-info {
  flex: 1;
}

.step-label {
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: #444;
}

.error-text {
  color: #FF4500;
  margin-top: 24px;
  font-size: 0.9rem;
  border: 2px solid #FF4500;
  padding: 12px;
}
</style>
