<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <td class="pt-4">
    <span
        class="badge fs-6 ms-1 mb-1 float-end"
        :style="{ 'background-color': colorFromGradient(prediction.prediction_score) }">
      {{ roundScore(prediction.prediction_score) }}%
    </span>
    <span v-html="output" />
  </td>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('span-extraction', {
  props: ['prediction', 'showWithContext'],
  mixins: [mixin],
  computed: {
    output() {
      let output = this.prediction.prediction_output.output
      if (this.showWithContext) {
        // If there is a prediction document returned use that and ignore local context
        output = this.prediction.prediction_documents[0].document
        // There can be an empty prediction document returned from the skill so use the local context instead
        if (output.length === 0 && this.$store.state.currentContext.length > 0) {
          output = this.$store.state.currentContext
        }
        output = this.highlightSpan(output, this.prediction.prediction_documents[0].span)
      }
      return output
    }
  },
  methods: {
    highlightSpan: function (doc, span) {
      if (span && span[0] !== span[1]) {
        return doc.slice(0, span[0]) + '<mark class="bg-success text-light">' + doc.slice(span[0], span[1]) + '</mark>' + doc.slice(span[1])
      } else {
        return doc
      }
    }
  }
})
</script>
