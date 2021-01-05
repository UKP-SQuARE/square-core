/**
 * Vue Router. All routes are managed here.
 */
import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import About from '@/views/About.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import Skills from '@/views/Skills.vue'
import Skill from '@/views/Skill.vue'
import Home from '@/views/Home.vue'
import Train from '@/views/Train.vue'
import ResetPassword from "../views/ResetPassword";
import ForgotPassword from "../views/ForgotPassword";
import ConfirmEmailLanding from "../views/ConfirmEmailLanding";
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/register',
    name: 'register',
    component: Register
  },
  {
    path: '/confirmEmailLanding/:token',
    name: 'confirmEmailLanding',
    component: ConfirmEmailLanding
  },
  {
    path: '/resetPassword/:token',
    name: 'resetPassword',
    component: ResetPassword,
    params: true
  },
  {
    path: '/forgotPassword',
    name: 'forgotPassword',
    component: ForgotPassword
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
    beforeEnter(to, frm, next) {
      if (!store.getters.isAuthenticated()) {
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
    beforeEnter(to, frm, next) {
      if (!store.getters.isAuthenticated()) {
        next("/login")
      } else {
        next()
      }
    }
  },
  {
    path: '/train/:id',
    name: 'train',
    component: Train,
    beforeEnter(to, frm, next) {
      if (!store.getters.isAuthenticated()) {
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
