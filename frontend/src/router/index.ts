import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/garments'
  },
  {
    path: '/garments',
    name: 'garments',
    component: () => import('@/views/Garments.vue'),
    meta: { title: '衣物档案', icon: 'Female' }
  },
  {
    path: '/storage',
    name: 'storage',
    component: () => import('@/views/Storage.vue'),
    meta: { title: '收纳分区', icon: 'Box' }
  },
  {
    path: '/wash-records',
    name: 'wash-records',
    component: () => import('@/views/WashRecords.vue'),
    meta: { title: '洗护记录', icon: 'Brush' }
  },
  {
    path: '/reminders',
    name: 'reminders',
    component: () => import('@/views/Reminders.vue'),
    meta: { title: '更换提醒', icon: 'Bell' }
  },
  {
    path: '/trip-plans',
    name: 'trip-plans',
    component: () => import('@/views/TripPlans.vue'),
    meta: { title: '出行清单', icon: 'Suitcase' }
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '数据统计', icon: 'DataLine' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || ''} - 内衣收纳与洗护管理`
  next()
})

export default router
