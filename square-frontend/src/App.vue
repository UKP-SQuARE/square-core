<!-- The Main View -->
<template>
  <div id="app" class="d-flex flex-column h-100">
    <NavBar />
    <div class="mb-4 bg-light border-bottom">
      <div class="container-fluid py-5 text-center">
        <h1 class="display-5 fw-light">SQuARE</h1>
        <p class="fs-4">QA Platform</p>
      </div>
    </div>
    <main class="flex-fill">
      <router-view class="container-xl h-100" />
    </main>
    <Footer />
  </div>
</template>

<script>
import Vue from 'vue'
import NavBar from '@/components/NavBar.vue'
import Footer from '@/components/Footer.vue'

export default Vue.component('app', {
  components: {
    NavBar,
    Footer
  },
  beforeMount() {
    this.$store.dispatch('initJWTfromLocalStorage')
  }
})
</script>

<style lang='scss'>
    .highlightText {
        background: yellow
    }
    @import "~bootstrap/scss/bootstrap";
</style>
