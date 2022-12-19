<template>
  <div>
    <div>This is the Place to start evaluations</div>
    <router-link class='btn btn-primary' to='/leaderboard' exact-active-class='active'>Go here to compare results!</router-link>
  </div>
</template>


<script>
import Vue from 'vue'

export default Vue.component('do-evaluation', {
   data() {
    return {}
  },
})
</script>
