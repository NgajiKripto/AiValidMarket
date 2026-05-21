<template>
  <div class="session-detail-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
        <div class="nav-links">
          <router-link to="/memory" class="nav-link">Memory</router-link>
          <a
            href="https://github.com/NgajiKripto/AiValidMarket"
            target="_blank"
            rel="noopener noreferrer"
            class="nav-link"
          >
            GitHub
          </a>
        </div>
      </div>
    </nav>

    <main class="content" v-if="session">
      <router-link to="/memory" class="back-link">Back to Memory</router-link>

      <h1 class="page-title">Session Detail</h1>

      <section class="detail-section">
        <h2 class="section-label">Idea</h2>
        <p class="idea-text">{{ session.idea_text }}</p>
      </section>

      <section class="detail-section" v-if="session.summary">
        <h2 class="section-label">Summary</h2>
        <p class="summary-text">{{ session.summary }}</p>
      </section>

      <section class="meta-section">
        <div class="meta-item">
          <span class="meta-label">Status</span>
          <span class="meta-value" :class="'status-' + session.status">{{ session.status }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Started</span>
          <span class="meta-value">{{ formatDate(session.started_at) }}</span>
        </div>
        <div class="meta-item" v-if="session.ended_at">
          <span class="meta-label">Ended</span>
          <span class="meta-value">{{ formatDate(session.ended_at) }}</span>
        </div>
      </section>

      <section class="memories-section" v-if="session.memories && session.memories.length > 0">
        <h2 class="section-label">Memories</h2>
        <div class="memories-list">
          <div v-for="(memory, i) in session.memories" :key="i" class="memory-card">
            <div class="memory-header">
              <span class="type-badge">{{ memory.type }}</span>
            </div>
            <p class="memory-content">{{ memory.content }}</p>
          </div>
        </div>
      </section>
    </main>

    <main class="content" v-else-if="error">
      <p class="error-text">{{ error }}</p>
      <router-link to="/memory" class="back-link">Back to Memory</router-link>
    </main>

    <main class="content loading-state" v-else>
      <div class="skeleton-block skeleton-title"></div>
      <div class="skeleton-block skeleton-body"></div>
      <div class="skeleton-block skeleton-body short"></div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSessionDetail } from '@/api/memory'

const route = useRoute()
const sessionId = route.params.sessionId

const session = ref(null)
const error = ref('')

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  try {
    const response = await getSessionDetail(sessionId)
    session.value = response.data
  } catch (err) {
    error.value = 'Failed to load session details.'
  }
})
</script>

<style scoped>
.session-detail-view {
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
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
  flex: 1;
  width: 100%;
}

.back-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: var(--space-6);
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

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-8);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.detail-section {
  margin-bottom: var(--space-8);
}

.section-label {
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.idea-text {
  font-size: var(--text-base);
  color: var(--color-text);
  line-height: var(--leading-relaxed);
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.summary-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.meta-section {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-6);
  padding: var(--space-4) var(--space-6);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-8);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.meta-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.meta-value {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

.status-completed {
  color: var(--color-success);
}

.status-active {
  color: var(--color-accent);
}

.status-failed {
  color: var(--color-error);
}

.memories-section {
  margin-bottom: var(--space-8);
}

.memories-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.memory-card {
  padding: var(--space-4);
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.memory-header {
  margin-bottom: var(--space-2);
}

.type-badge {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
  background: var(--color-accent-subtle);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.memory-content {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}

.error-text {
  color: var(--color-error);
  font-size: var(--text-sm);
  padding: var(--space-3) var(--space-4);
  background: var(--color-error-bg);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-4);
}

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

  .meta-section {
    flex-direction: column;
    gap: var(--space-3);
  }
}
</style>
