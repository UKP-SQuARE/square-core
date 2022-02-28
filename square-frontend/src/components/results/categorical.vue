<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <td class="pt-4">
    <div class="d-flex flex-column align-items-center">
    <div
        class="d-inline-flex align-items-center justify-content-center fs-2 rounded-circle bg-primary"
        style="width: 3.5rem; height: 3.5rem;"
        :title="prediction.prediction_output.output">
      {{ {true: '👍', false: '👎'}[output] }}
    </div>
    <span
        class="badge fs-6 mt-2"
        :style="{ 'background-color': colorFromGradient(prediction.prediction_score) }">
      {{ roundScore(prediction.prediction_score) }}%
    </span>
    </div>
  </td>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('categorical-results', {
  props: ['prediction'],
  mixins: [mixin],
  computed: {
    output() {
      return this.prediction.prediction_output.output === 'yes'
    }
  }
})
</script>
