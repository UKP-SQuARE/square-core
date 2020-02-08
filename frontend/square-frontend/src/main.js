import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import BootstrapVue from 'bootstrap-vue'
import axios from 'axios'

Vue.config.productionTip = false

// Install BootstrapVue
Vue.use(BootstrapVue)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

axios.interceptors.response.use((response) => {
    return response;
  }, (err) => {
    const error = err.response;

    if (error.status === 401 && error.config && !error.config.__isRetryRequest) {
          router.push("/login")
          return Promise.reject(error)
    }
    return Promise.reject(error)
  })
