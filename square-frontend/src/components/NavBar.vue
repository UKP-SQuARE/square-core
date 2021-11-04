<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <header class="p-2 bg-primary">
    <div class="container">
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
          <router-link class="navbar-brand" to="/">SQuARE</router-link>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon" />
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <router-link class="nav-link active" aria-current="page" to="/">Home</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/about">About</router-link>
              </li>
            </ul>
            <div class="text-end" v-if="!isAuthenticated">
              <router-link to="/login" role="button" class="btn btn-outline-light me-2">Sign in</router-link>
              <router-link to="/register" role="button" class="btn btn-light">Sign up</router-link>
            </div>
            <div class="dropdown text-end" v-else>
              <a href="#" class="d-block text-white text-decoration-none dropdown-toggle" id="dropdownUser1" data-bs-toggle="dropdown" aria-expanded="false">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person" viewBox="0 0 16 16">
                  <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
                </svg>
                {{ user.name }}
              </a>
              <ul class="dropdown-menu text-small" aria-labelledby="dropdownUser1">
                <li><a class="dropdown-item" href="/skills">My Skills</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" v-on:click.prevent="signout" href="#">Sign out</a></li>
              </ul>
            </div>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
import Vue from 'vue'

export default Vue.component('nav_bar', {
  computed: {
    user() {
      return this.$store.state.user
    },
    isAuthenticated() {
      return this.$store.getters.isAuthenticated()
    }
  },
  methods: {
    signout() {
      this.$store.dispatch('signout')
          .then(() => this.$router.push('/'))
    }
  }
})
</script>
