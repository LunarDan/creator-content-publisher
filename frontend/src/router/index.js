import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ContentEditor from '../views/ContentEditor.vue'
import AdaptationCenter from '../views/AdaptationCenter.vue'
import PreviewCenter from '../views/PreviewCenter.vue'
import PublishCenter from '../views/PublishCenter.vue'
import PublishHistory from '../views/PublishHistory.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard },
  { path: '/content-editor', component: ContentEditor },
  { path: '/adaptation-center', component: AdaptationCenter },
  { path: '/preview-center', component: PreviewCenter },
  { path: '/publish-center', component: PublishCenter },
  { path: '/publish-history', component: PublishHistory },
  { path: '/settings', component: Settings },
]

export default createRouter({ history: createWebHistory(), routes })
