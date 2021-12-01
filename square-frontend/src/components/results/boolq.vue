<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div class="d-flex">
    <div class="d-flex flex-column align-items-center">
      <div
          class="d-inline-flex align-items-center justify-content-center fs-2 bg-danger rounded-circle"
          style="width: 3.5rem; height: 3.5rem;">👎</div>
      <span class="badge bg-transparent text-dark border border-danger mt-2 p-2">{{ currentResults.no }}%</span>
    </div>
    <div class="progress flex-grow-1 align-self-center mx-2">
      <div
          class="progress-bar bg-danger"
          role="progressbar"
          :style="{ width: `${currentResults.no}%` }"
          :aria-valuenow="currentResults.no"
          aria-valuemin="0"
          aria-valuemax="100" />
      <div
          class="progress-bar bg-success"
          role="progressbar"
          :style="{ width: `${currentResults.yes}%` }"
          :aria-valuenow="currentResults.yes"
          aria-valuemin="0"
          aria-valuemax="100" />
    </div>
    <div class="d-flex flex-column align-items-center">
      <div
          class="d-inline-flex align-items-center justify-content-center fs-2 bg-success rounded-circle"
          style="width: 3.5rem; height: 3.5rem;">👍</div>
      <span class="badge bg-transparent text-dark border border-success mt-2 p-2">{{ currentResults.yes }}%</span>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('boolq-results', {
  props: ['skillResult'],
  mixins: [mixin],
  computed: {
    currentResults() {
      let result = {}
      this.skillResult.results.forEach(res => {
        result[res.prediction_output.output] = this.roundScore(res.prediction_output.output_score)
      })
      return result
    }
  }
})
</script>
