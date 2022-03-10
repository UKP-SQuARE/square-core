<!-- The Login Page. The user can login here. -->
<template>
  <div class="d-flex align-items-center">
    <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
      <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
        <div class="mb-3 pb-3">
          <div class="feature-icon bg-danger bg-gradient">
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-key" viewBox="0 0 16 16">
              <path d="M0 8a4 4 0 0 1 7.465-2H14a.5.5 0 0 1 .354.146l1.5 1.5a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0L13 9.207l-.646.647a.5.5 0 0 1-.708 0L11 9.207l-.646.647a.5.5 0 0 1-.708 0L9 9.207l-.646.647A.5.5 0 0 1 8 10h-.535A4 4 0 0 1 0 8zm4-3a3 3 0 1 0 2.712 4.285A.5.5 0 0 1 7.163 9h.63l.853-.854a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708 0l.646.647.793-.793-1-1h-6.63a.5.5 0 0 1-.451-.285A3 3 0 0 0 4 5z"/>
              <path d="M4 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
            </svg>
          </div>
          <h2 class="display-5">Please sign in</h2>
          <p class="lead fs-2">You need an account to access this page</p>
          <div class="d-grid gap-2 d-flex justify-content-center">
            <a v-on:click.prevent="signIn" href="#" class="btn btn-outline-danger btn-lg px-4">Sign in</a>
            <a v-on:click.prevent="signUp" href="#" class="btn btn-danger btn-lg text-white px-4">Sign up</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('sign-in', {
  props: ['keycloak'],
  methods: {
    signIn() {
      this.keycloak.login({redirectUri: `${window.location.origin}`})
    },
    signUp() {
      this.keycloak.register({redirectUri: `${window.location.origin}`})
    }
  }
})
</script>