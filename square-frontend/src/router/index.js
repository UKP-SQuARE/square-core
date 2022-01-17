/**
 * Vue Router. All routes are managed here.
 */
import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import About from '@/views/About.vue'
import Signup from '@/views/Signup.vue'
import Signin from '@/views/Signin.vue'
import Skills from '@/views/Skills.vue'
import Skill from '@/views/Skill.vue'
import Home from '@/views/Home.vue'
import Train from '@/views/Train.vue'
import Explain from '@/views/Explain.vue'
import NotFound from '@/views/NotFound.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/signup',
    name: 'signup',
    component: Signup
  },
  {
    path: '/signin',
    name: 'signin',
    component: Signin,
    beforeEnter(to, from, next) {
      if (!store.getters.isAuthenticated()) {
        next()
      } else {
        // If already signed in navigate to root
        next('/')
      }
    }
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
    path: '/train/:id',
    name: 'train',
    component: Train,
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
    path: '/about',
    name: 'about',
    component: About
  },
  {
    path: '*',
    name: 'notfound',
    component: NotFound
  }
]

const router = new VueRouter({
  routes,
  mode: 'history'
})

export default router
