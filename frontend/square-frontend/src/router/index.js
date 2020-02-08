import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import Query from '../views/Query.vue'
import Results from '../views/Results.vue'
import About from '@/views/About.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import Skills from '@/views/Skills.vue'
import Skill from '@/views/Skill.vue'
import Home from '@/views/Home.vue'
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    children: [  
      {
        path: '/',
        name: 'query',
        component: Query
      },
      {
        path: '/results',
        name: 'results',
        component: Results
      }
    ]
  },
  {
    path: '/register',
    name: 'register',
    component: Register
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/skills',
    name: 'skills',
    component: Skills,
    beforeEnter (to, frm, next) {
      if (!store.getters.isAuthenticated) {
        next("/login")
      } else {
        next()
      }
    }
  },
  {
    path: '/skills/:id',
    name: 'skill',
    component: Skill,
    beforeEnter (_, __, next) {
      if (!store.getters.isAuthenticated) {
        next("/login")
      } else {
        next()
      }
    }
  },
  {
    path: '/about',
    name: 'about',
    component: About
  }
]

const router = new VueRouter({
  routes
})

export default router
