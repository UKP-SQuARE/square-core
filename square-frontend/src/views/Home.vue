<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <Query />
    <Results />
  </div>
</template>

<script>
import Vue from 'vue'
import Query from '@/components/Query.vue'
import Results from '@/components/Results.vue'

export default Vue.component('square-home', {
  components: {
    Query,
    Results
  }
})
</script>