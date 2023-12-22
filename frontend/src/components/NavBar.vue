<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <header class="bg-primary">
    <div class="container-lg">
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
          <router-link class="navbar-brand d-flex align-items-center" to="/">
            <img :src="`${publicPath}SQ_Web_Light_90px.png`" alt="UKP-SQuARE" width="45" height="45">
            &nbsp;UKP-SQuARE
          </router-link>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon" />
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto">
              <li class="nav-item">
                <router-link class="nav-link" to="/qa_hub" exact-active-class="active">QA Hub</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/behavioral_tests" exact-active-class="active">Behavioral
                  Tests</router-link>
              </li>
            <!-- <li class="nav-item">
                <router-link class="nav-link" to="/leaderboard" exact-active-class="active">Leaderboard</router-link>
                                    </li> -->
              <li class="nav-item">
                <router-link class="nav-link" to="/publications" exact-active-class="active">Publications</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link btn btn-danger" to="/chatbot_rating" exact-active-class="active">1) ChatBot Rating</router-link>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="/docs/" target="_blank">Docs</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="/news/">News</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="https://github.com/UKP-SQuARE/square-core" title="GitHub" target="_blank">
                  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor"
                    class="bi bi-github" viewBox="0 0 16 21">
                    <path
                      d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                  </svg> GitHub
                </a>
              </li>
            </ul>

            <div class="text-end" v-if="!isAuthenticated">
              <a v-on:click.prevent="$emit('sign-in')" href="#" role="button" class="btn btn-outline-light me-2">Sign
                in</a>
              <a v-on:click.prevent="$emit('sign-up')" href="#" role="button" class="btn btn-light">Sign up</a>
            </div>
            <div class="dropdown text-end" v-else>
              <a href="#" class="btn btn-outline-light dropdown-toggle d-inline-flex align-items-center"
                id="dropdownUser1" data-bs-toggle="dropdown" aria-expanded="false">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor"
                  class="bi bi-person-fill" viewBox="0 0 16 16">
                  <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
                </svg>
                &nbsp;{{ userInfo.preferred_username }}
              </a>
              <!-- <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <ul class="navbar-nav me-auto">
                <li class="nav-item">

                  <router-link class="nav-link" to="/profile" exact-active-class="active">Profile</router-link>
                </li>
              </ul> -->
              <ul class="dropdown-menu dropdown-menu-end">
                <!-- <li><router-link class="dropdown-item" to="/skills">My skills</router-link></li>
                <li><router-link class="dropdown-item" to="/evaluations">Evaluate skills</router-link></li> -->
                <li><router-link class="dropdown-item" to="/profile">My Profile</router-link></li>
                <!-- <li><a v-on:click.prevent="$emit('account')" href="#" class="dropdown-item">Manage account</a></li> -->
                <li>
                  <hr class="dropdown-divider">
                </li>
                <li><a v-on:click.prevent="$emit('sign-out')" href="#" class="dropdown-item">Sign out</a></li>
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

export default Vue.component('nav-bar', {
  data() {
    return {
      publicPath: process.env.BASE_URL
    }
  },
  computed: {
    userInfo() {
      return this.$store.state.userInfo
    },
    isAuthenticated() {
      return Object.keys(this.$store.state.userInfo).length > 0
    }
  }
})
</script>

<style >
#separator {
  margin: 5px 10px;
  border-right: 1px solid rgb(255, 255, 255);
}
</style>