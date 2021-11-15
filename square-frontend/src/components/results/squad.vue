<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <ul class="list-group list-group-flush">
    <li
        v-for="(res, index) in skillResult.results"
        :key="index"
        class="list-group-item">
      <div class="d-flex w-100 justify-content-between align-items-start mb-2">
        <div>{{ index + 1 }}. Answer: <span class="fw-bold">{{ res.prediction_output.output }}</span></div>
        <span class="badge bg-primary p-2">{{ roundScore(res.prediction_score) }}%</span>
      </div>
      <small v-html="highlightSpan(res.prediction_documents[0].document, res.prediction_documents[0].span)" />
      <div class="progress mt-2">
        <div
            class="progress-bar progress-bar-striped bg-primary"
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

export default Vue.component('squad', {
  props: ['skillResult'],
  mixins: [mixin]
})
</script>
