/**
 * Code entry point. Initilize Vue and any other JS components that need it.
 */
import Vue from 'vue'
import App from './App.vue'
import * as bootstrap from 'bootstrap'
import router from './router'
import store from './store'
import axios from 'axios'

Vue.use(bootstrap)

// Init Vue
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

// Configure Axios so that any 401 responses results in a redirect to the login page
axios.interceptors.response.use((response) => {
    return response
  }, (err) => {
    const error = err.response
    if (error.status === 401 && error.config && !error.config.__isRetryRequest) {
          router.push('/login')
          return Promise.reject(error)
    }
    return Promise.reject(error)
  })
