/**
 * Vue Router. All routes are managed here.
 */
import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

// Use lazy loading to improve page size
const Home = () => import('../views/Home')
const QA = () => import('../views/QA')
const Explain = () => import('../views/Explain')
const Skills = () => import('../views/Skills')
const Skill = () => import('../views/Skill')
const Feedback = () => import('../views/Feedback')
const NotFound = () => import('../views/NotFound')

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/qa',
    name: 'qa',
    component: QA
  },
  {
    path: '/skills',
    name: 'skills',
    component: Skills,
    beforeEnter(to, from, next) {
      if (!store.getters.isAuthenticated()) {
        next('/signin')
      } else {
        next()
      }
    }
  },
  {
    path: '/skills/:id',
    name: 'skill',
    component: Skill,
    beforeEnter(to, from, next) {
      if (!store.getters.isAuthenticated()) {
        next('/signin')
      } else {
        next()
      }
    }
  },
  {
    path: '/explain',
    name: 'explain',
    component: Explain
  },
  {
    path: '/feedback',
    name: 'feedback',
    component: Feedback
  },
  {
    path: '*',
    name: 'notfound',
    component: NotFound
  }
]

const router = new VueRouter({
  routes,
  mode: 'history',
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  }
})

router.beforeEach((to, from, next) => {
  if ('state' in to.query && 'session_state' in to.query && 'code' in to.query) {
    console.log(to.query)
    store.dispatch('signIn', {
      code: to.query.code,
      redirectURI: to.query.redirect_uri,
      clientId: to.query.client_id
    }).then(() => {
      router.replace({ query: {} })
    })
  }
  next()
})

export default router
