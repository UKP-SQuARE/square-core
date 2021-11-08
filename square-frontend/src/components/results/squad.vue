<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <ol class="list-group list-group-numbered list-group-flush">
    <li
        v-for="(res, index) in skillResult.results"
        :key="index"
        class="list-group-item d-flex justify-content-between align-items-start">
      <div class="ms-2 me-auto">
        <div class="fw-bold">Answer: {{ res.prediction_output.output }}</div>
        <small v-html="highlightSpan(res.prediction_documents[0].document, res.prediction_documents[0].span)" />
      </div>
      <span class="badge bg-primary rounded-pill">{{ roundScore(res.prediction_score) }}%</span>
    </li>
  </ol>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('squad', {
  props: ['skillResult'],
  mixins: [mixin]
})
</script>
