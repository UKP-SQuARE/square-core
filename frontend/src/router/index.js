/**
 * Vue Router. All routes are managed here.
 */
import Vue from 'vue'
import VueRouter from 'vue-router'

// Use lazy loading to improve page size
const Home = () => import('../views/Home')
const QA = () => import('../views/QA')
const BehavioralTests = () => import('../views/BehavioralTests')
const Skills = () => import('../views/Skills')
const Skill = () => import('../views/Skill')
const Evaluations = () => import('../views/Evaluations')
const Leaderboard = () => import('../views/Leaderboard')
const Feedback = () => import('../views/Feedback')
const Terms = () => import('../views/Terms')
const News = () => import('../views/News')
const Publications = () => import('../views/Publications')
const SignIn = () => import('../views/SignIn')
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
    meta: {
      requiresAuthentication: true
    }
  },
  {
    path: '/skills/:id',
    name: 'skill',
    component: Skill,
    meta: {
      requiresAuthentication: true
    }
  },
  {
    path: '/evaluations',
    name: 'evaluations',
    component: Evaluations,
    meta: {
      requiresAuthentication: true
    }
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: Leaderboard
  },
  {
    path: '/behavioral_tests',
    name: 'behavioral_tests',
    component: BehavioralTests
  },
  {
    path: '/feedback',
    name: 'feedback',
    component: Feedback
  },
  {
    path: '/news',
    name: 'news',
    component: News
  },
  {
    path: '/publications',
    name: 'publications',
    component: Publications
  },
  {
    path: '/terms-and-conditions',
    name: 'terms',
    component: Terms
  },
  {
    path: '/signin',
    name: 'signIn',
    component: SignIn
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

export default router
