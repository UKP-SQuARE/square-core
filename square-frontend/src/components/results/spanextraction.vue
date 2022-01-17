<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div>
    <div class="row">
      <div class="col-xl col-lg-7 mb-4 mb-lg-0">
        <ul class="list-group list-group-flush">
          <li
              v-for="(res, index) in skillResult.predictions"
              :key="index"
              v-on:mouseover="activeResult = index"
              class="list-group-item list-group-item-action"
              :class="{ 'border-primary': index === activeResult, 'bg-light': index === activeResult }"
              :aria-current="index === activeResult">
            <div class="d-flex w-100 justify-content-between align-items-start">
              <div class="d-flex align-items-baseline">
                <h5
                    class="m-0"
                    :class="{ 'text-primary': index === activeResult }">{{ index + 1 }}.</h5>
                <small class="mx-2">{{ res.prediction_output.output }}</small>
              </div>
              <span class="badge bg-transparent text-dark border border-primary p-2">{{ roundScore(res.prediction_score) }}%</span>
            </div>
          </li>
        </ul>
      </div>
      <div class="col-xl col-lg-5">
        <div class="border rounded bg-light p-4" v-html="currentContext" />
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('span-extraction-results', {
  props: ['skillResult'],
  mixins: [mixin],
  data() {
    return {
      activeResult: 0
    }
  },
  computed: {
    currentContext: function () {
      let document = ''
      if (this.$store.state.currentContext.length > 0) {
        document = this.$store.state.currentContext
      } else {
        document = this.skillResult.predictions[this.activeResult].prediction_documents[0].document
      }
      return this.highlightSpan(document, this.skillResult.predictions[this.activeResult].prediction_documents[0].span)
    }
  }
})
</script>
