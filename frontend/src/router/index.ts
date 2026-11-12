import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { authState } from '@/auth/session'
import { initializeSession } from '@/api/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/AuthView.vue') },
    { path: '/register', name: 'register', component: () => import('@/views/AuthView.vue') },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'lessons', name: 'lessons', component: () => import('@/views/LessonsView.vue'), meta: { requiresAuth: true } },
        { path: 'lessons/:id', name: 'grammar-lesson', component: () => import('@/views/GrammarLessonView.vue'), meta: { requiresAuth: true } },
        { path: 'lessons/:id/quiz', component: () => import('../views/QuizView.vue'), meta: { requiresAuth: true } },
        { path: 'alphabet', name: 'alphabet', component: () => import('@/views/AlphabetView.vue'), meta: { requiresAuth: true } },
        { path: 'practice', component: () => import('../views/PracticeHubView.vue'), meta: { requiresAuth: true } },
        { path: 'practice/session', component: () => import('../views/PracticeSessionView.vue'), meta: { requiresAuth: true } },
        { path: 'admin', name: 'admin', component: () => import('@/views/AdminView.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      ],
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})

router.beforeEach(async (to) => {
  if (!authState.initialized) initializeSession()
  if (to.meta.requiresAuth && !authState.user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && authState.user?.role !== 'admin') return { name: 'home' }
  if ((to.name === 'login' || to.name === 'register') && authState.user) return { name: 'home' }
  return true
})

export { router }