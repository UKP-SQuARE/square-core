<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <div class="alert alert-warning" role="alert"
      v-if="this.$store.state.skillOptions['qa']['selectedSkills'].includes('62eb8f7765872e7b65ea5c8b')">
      QAGNN is intrinsically slower than the other skills. On average, it takes 20s to run. Please be patient.
    </div>
    <Query ref="query" :selectedSkills="selectedSkills" />
    <Results v-if="isShowingResults" :selectedSkills="selectedSkills" />
  </div>
</template>

<script>
/* eslint-disable */
import Vue from 'vue'
import Query from '@/components/Query.vue'
import Results from '@/components/Results.vue'

export default Vue.component('run-qa', {
  components: {
    Query,
    Results
  },
  computed: {
    selectedSkills() {
      let selectedSkills = []
      for (const [key, value] of Object.entries(this.$route.query)) {
        // if key is of the shape "skill<number>"
        if (key.startsWith("skill")) {
          selectedSkills.push(value)
        }
      }
      return selectedSkills
    },
    isShowingResults() {

      return this.$store.state.currentResults.length > 0
    }
  },
  beforeMount() {
    if (this.$store.availableSkills === undefined) {
      this.$store.dispatch('updateSkills')
    }
  },
  beforeRouteLeave: function (to, from, next) {
    this.$refs.query.prepareToExit()
    this.$store.commit('setAnsweredQuestion', {
      results: "",
      question: "",
      context: "",
      choices: [],
      currentSkills: []
    })

    // Make sure to always call the next function, otherwise the hook will never be resolved
    // Ref: https://router.vuejs.org/en/advanced/navigation-guards.html
    next();
  }
})
</script>