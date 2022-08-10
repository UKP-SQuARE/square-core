<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <div class="alert alert-warning" role="alert" v-if="this.$store.state.skillOptions['qa']['selectedSkills'].includes('62eb8f7765872e7b65ea5c8b')">
      QAGNN is intrinsically slower than the other skills. On average, it takes 20s to run. Please, be patient.
    </div>
    <Query />
    <Results v-if="isShowingResults" />
    <div v-else class="row">
      <div class="col-md-8 mx-auto mt-4 text-center">
        <div class="bg-light border rounded shadow p-5 text-center">
          <div class="feature-icon bg-danger bg-gradient">
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-question-lg" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M4.475 5.458c-.284 0-.514-.237-.47-.517C4.28 3.24 5.576 2 7.825 2c2.25 0 3.767 1.36 3.767 3.215 0 1.344-.665 2.288-1.79 2.973-1.1.659-1.414 1.118-1.414 2.01v.03a.5.5 0 0 1-.5.5h-.77a.5.5 0 0 1-.5-.495l-.003-.2c-.043-1.221.477-2.001 1.645-2.712 1.03-.632 1.397-1.135 1.397-2.028 0-.979-.758-1.698-1.926-1.698-1.009 0-1.71.529-1.938 1.402-.066.254-.278.461-.54.461h-.777ZM7.496 14c.622 0 1.095-.474 1.095-1.09 0-.618-.473-1.092-1.095-1.092-.606 0-1.087.474-1.087 1.091S6.89 14 7.496 14Z"/>
            </svg>
          </div>
          <h2 class="display-5">Question Answering</h2>
          <p class="lead fs-2">Try <span class="text-danger">extractive</span>, <span class="text-danger">multiple choice</span>, and <span class="text-danger">categorical</span> skills.</p>
          <p class="lead fs-2">Enter your own questions or pick one of the examples.</p>
          <p class="lead fs-2"><span class="text-danger">Get started</span> by selecting up to three skills.</p>
        </div>
      </div>
    </div>
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
  },
  computed: {
    isShowingResults() {

      return this.$store.state.currentResults.length > 0
    }
  }
})
</script>