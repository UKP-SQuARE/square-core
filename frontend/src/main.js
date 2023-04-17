/**
 * Code entry point. Initialize Vue and any other JS components that need it.
 */
import Vue from 'vue'
import App from './App.vue'
import * as bootstrap from 'bootstrap'
import router from './router'
import store from './store'
import Keycloak from 'keycloak-js'

Vue.use(bootstrap)

let initOptions = {
  url: `${process.env.VUE_APP_KEYCLOAK_URL}/auth`,
  realm: 'square',
  clientId: 'web-app',
  onLoad: 'check-sso',
  silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
}
let keycloak = Keycloak(initOptions)
keycloak.init({
  checkLoginIframe: false,
}).then((authenticated) => {
  if (process.env.VUE_APP_AUTH_TOKEN !== '') {
    keycloak.authenticated = true
    authenticated = true
    keycloak.token = process.env.VUE_APP_AUTH_TOKEN
    store.dispatch('signIn', { userInfo: { 'preferred_username': 'LOCAL_SQUARE_USER' }, token: process.env.VUE_APP_AUTH_TOKEN })
  } else if (authenticated) {
    keycloak.loadUserInfo().then(userInfo => {
      store.dispatch('signIn', { userInfo: userInfo, token: keycloak.token })
    })
    setInterval(() => {
      keycloak.updateToken(70).then(() => {
        store.dispatch('refreshToken', { token: keycloak.token })
      })
    }, 6000)
  }
})

// Init Vue
new Vue({
  router,
  store,
  render: h => h(App, { props: { keycloak: keycloak } })
}).$mount('#app')
