import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/validate/:taskId',
    name: 'ValidationView',
    component: () => import('@/views/ValidationView.vue')
  },
  {
    path: '/results/:taskId',
    name: 'ResultsView',
    component: () => import('@/views/ResultsView.vue')
  },
  {
    path: '/memory',
    name: 'MemoryView',
    component: () => import('@/views/MemoryView.vue')
  },
  {
    path: '/memory/session/:sessionId',
    name: 'SessionDetailView',
    component: () => import('@/views/SessionDetailView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
