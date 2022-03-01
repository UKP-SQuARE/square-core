/**
 * Code entry point. Initialize Vue and any other JS components that need it.
 */
import Vue from 'vue'
import App from './App.vue'
import * as bootstrap from 'bootstrap'
import router from './router'
import store from './store'

Vue.use(bootstrap)

// Init Vue
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
