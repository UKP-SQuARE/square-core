/**
 * Code entry point. Initilize Vue and any other JS components that need it.
 */
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import BootstrapVue from 'bootstrap-vue'
import axios from 'axios'
import Vuex from 'vuex';
import VueSocketIO from 'vue-socket.io';

Vue.config.productionTip = false

// Install BootstrapVue
Vue.use(BootstrapVue)

// Set Vue to use Vuex
Vue.use(Vuex);

// Set Vue to use VueSocketIO with Vuex integration
Vue.use(new VueSocketIO({
    debug: true,
    connection: process.env.VUE_APP_BACKEND_URL,
    vuex: {
        store,
        actionPrefix: "SOCKET_",
        mutationPrefix: 'SOCKET_'
    }
}));

// Init Vue
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

// Configure Axios so that any 401 responses result in a redirect to the login page
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
