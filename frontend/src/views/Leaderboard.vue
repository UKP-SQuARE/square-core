<template>
  <div>
    <div>This is the Leaderboard</div>
    <router-link class='btn btn-primary' to='/evaluation' exact-active-class='active'>Evaluate your skills now!</router-link>
  </div>
</template>


<script>
import Vue from 'vue'

export default Vue.component('show-leaderboard', {
   data() {
    return {}
  },
})
</script>
