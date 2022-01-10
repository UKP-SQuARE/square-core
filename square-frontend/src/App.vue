<!-- The Main View -->
<template>
  <div id="app" class="d-flex flex-column h-100">
    <NavBar />
    <div class="mb-4 bg-light border-bottom">
      <div class="container-fluid py-5 text-center">
        <img class="d-block mx-auto mb-2" :src="`${publicPath}SQ_Web_Light_160px.png`" alt="" width="80" height="80">
        <h1 class="display-5 fw-light">UKP-SQuARE</h1>
        <p class="fs-4">Software for Question Answering Research</p>
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
  data() {
    return {
      publicPath: process.env.BASE_URL
    }
  },
  beforeMount() {
    this.$store.dispatch('initJWTfromLocalStorage')
  }
})
</script>

<style lang='scss'>
    $primary: #006691;

    @import "~bootstrap/scss/bootstrap";
</style>
