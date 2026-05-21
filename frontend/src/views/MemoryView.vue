<template>
  <div class="memory-view">
    <nav class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="brand">AIVALIDMARKET</router-link>
        <div class="nav-links">
          <router-link to="/memory" class="nav-link nav-link-active">Memory</router-link>
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

    <main class="content">
      <h1 class="page-title">Memory</h1>
      <p class="page-subtitle">Browse past validation sessions and search memories.</p>

      <div class="stats-bar" v-if="stats">
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_memories }}</span>
          <span class="stat-label">Total Memories</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_sessions }}</span>
          <span class="stat-label">Total Sessions</span>
        </div>
      </div>

      <section class="search-section">
        <div class="search-input-wrap">
          <input
            v-model="searchQuery"
            class="search-input"
            placeholder="Search memories..."
            aria-label="Search memories"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" :disabled="!searchQuery.trim()" @click="handleSearch">
            Search
          </button>
        </div>
      </section>

      <section v-if="searchResults.length > 0" class="search-results-section">
        <h2 class="section-title">Search Results</h2>
        <div class="results-list">
          <div v-for="(item, i) in searchResults" :key="i" class="result-card">
            <div class="result-header">
              <span class="type-badge">{{ item.entry.memory_type }}</span>
              <span class="relevance-score">Score: {{ item.relevance_score?.toFixed(2) }}</span>
            </div>
            <p class="result-content">{{ item.entry.summary || item.entry.content }}</p>
          </div>
        </div>
        <button class="clear-btn" @click="clearSearch">Clear Results</button>
      </section>

      <section class="sessions-section">
        <h2 class="section-title">Past Sessions</h2>
        <div v-if="sessions.length === 0 && !loading" class="empty-state">
          <p>No validation sessions found.</p>
        </div>
        <div v-else class="sessions-list">
          <router-link
            v-for="session in sessions"
            :key="session.id"
            :to="`/memory/session/${session.id}`"
            class="session-card"
          >
            <p class="session-idea">{{ truncate(session.idea_text, 120) }}</p>
            <div class="session-meta">
              <span class="session-date">{{ formatDate(session.started_at) }}</span>
              <span class="session-status" :class="'status-' + session.status">{{ session.status }}</span>
            </div>
          </router-link>
        </div>
      </section>

      <p v-if="error" class="error-text">{{ error }}</p>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMemorySessions, searchMemories, getMemoryStats } from '@/api/memory'

const stats = ref(null)
const sessions = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const error = ref('')

function truncate(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  error.value = ''
  try {
    const response = await searchMemories(searchQuery.value)
    searchResults.value = response.data || []
  } catch (err) {
    error.value = 'Search failed. Please try again.'
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
}

onMounted(async () => {
  loading.value = true
  try {
    const [statsRes, sessionsRes] = await Promise.all([
      getMemoryStats(),
      getMemorySessions()
    ])
    stats.value = statsRes.data
    sessions.value = sessionsRes.data || []
  } catch (err) {
    error.value = 'Failed to load memory data.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.memory-view {
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

.nav-link-active {
  background: oklch(0.3 0.01 170);
  border-color: oklch(0.5 0.01 170);
}

.content {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
  flex: 1;
  width: 100%;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.page-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
}

.stats-bar {
  display: flex;
  gap: var(--space-6);
  padding: var(--space-4) var(--space-6);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-8);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.search-section {
  margin-bottom: var(--space-8);
}

.search-input-wrap {
  display: flex;
  gap: var(--space-2);
}

.search-input {
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

.search-input:hover {
  border-color: oklch(0.75 0.03 170);
}

.search-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px oklch(0.55 0.14 170 / 0.12);
}

.search-btn {
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

.search-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.search-btn:active:not(:disabled) {
  background: var(--color-accent-active);
  border-color: var(--color-accent-active);
}

.search-btn:focus-visible {
  box-shadow: var(--focus-ring);
}

.search-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.search-results-section {
  margin-bottom: var(--space-8);
  padding: var(--space-6);
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-4);
  color: var(--color-text);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.result-card {
  padding: var(--space-4);
  background: var(--color-surface-raised);
  border-radius: var(--radius-md);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
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

.relevance-score {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

.result-content {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}

.clear-btn {
  margin-top: var(--space-4);
  padding: var(--space-2) var(--space-4);
  min-height: 44px;
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease);
}

.clear-btn:hover {
  background: var(--color-surface-raised);
  border-color: var(--color-accent);
}

.sessions-section {
  margin-bottom: var(--space-8);
}

.empty-state {
  padding: var(--space-8);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.session-card {
  display: block;
  padding: var(--space-4) var(--space-5);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-muted);
  transition: background var(--duration-fast) var(--ease),
              border-color var(--duration-fast) var(--ease),
              box-shadow var(--duration-fast) var(--ease);
}

.session-card:hover {
  background: var(--color-accent-subtle);
  border-color: var(--color-accent-muted);
  box-shadow: var(--shadow-sm);
}

.session-card:focus-visible {
  box-shadow: var(--focus-ring);
}

.session-idea {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: var(--space-2);
  line-height: var(--leading-normal);
}

.session-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.session-date {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.session-status {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.status-completed {
  color: var(--color-success);
  background: var(--color-accent-subtle);
}

.status-active {
  color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.status-failed {
  color: var(--color-error);
  background: var(--color-error-bg);
}

.error-text {
  color: var(--color-error);
  font-size: var(--text-sm);
  padding: var(--space-3) var(--space-4);
  background: var(--color-error-bg);
  border-radius: var(--radius-sm);
  margin-top: var(--space-4);
}

@media (max-width: 600px) {
  .content {
    padding: var(--space-8) var(--space-4);
  }

  .stats-bar {
    flex-direction: column;
    gap: var(--space-3);
  }

  .search-input-wrap {
    flex-direction: column;
  }
}
</style>
