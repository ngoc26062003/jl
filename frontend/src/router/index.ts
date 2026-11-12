import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'lessons', name: 'lessons', component: () => import('@/views/LessonsView.vue') },
        { path: 'lessons/:id', name: 'grammar-lesson', component: () => import('@/views/GrammarLessonView.vue') },
        { path: '/lessons/:id/quiz', component: () => import('../views/QuizView.vue') },
        { path: '/alphabet', name: 'alphabet', component: () => import('@/views/AlphabetView.vue') },
      
        { path: '/practice', component: () => import('../views/PracticeHubView.vue') },
        { path: '/practice/session', component: () => import('../views/PracticeSessionView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})