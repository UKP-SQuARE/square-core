<!-- The Main View -->
<template>
  <div id="app" class="d-flex flex-column h-100">
    <header>
      <NavBar />
      <b-jumbotron bg-variant="light" class="border-bottom rounded-0 text-center mb-0 p-4">
        <h1 class="font-weight-light">SQuARE</h1>
        <p class="lead">QA Platform</p>
      </b-jumbotron>
    </header>
    <main class="flex-fill">
      <router-view class="container border-left border-right shadow py-3 h-100" />
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
@import '~bootstrap';
@import '~bootstrap-vue';
</style>
