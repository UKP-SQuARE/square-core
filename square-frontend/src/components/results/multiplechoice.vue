<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <ul class="list-group list-group-flush">
    <li
        v-for="(res, index) in skillResult.predictions"
        :key="index"
        class="list-group-item">
      <div class="d-flex w-100 justify-content-between">
        <div>{{ index + 1 }}. <span class="fw-bold">{{ res.prediction_output.output }}</span></div>
        <span class="badge bg-transparent text-dark border border-primary p-2">{{ roundScore(res.prediction_score) }}%</span>
      </div>
      <div class="progress mt-2">
        <div
            class="progress-bar bg-primary"
            role="progressbar"
            :style="{ width: `${roundScore(res.prediction_score)}%` }"
            :aria-valuenow="roundScore(res.prediction_score)"
            aria-valuemin="0"
            aria-valuemax="100" />
      </div>
    </li>
  </ul>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('multiple-choice-results', {
  props: ['skillResult'],
  mixins: [mixin]
})
</script>
