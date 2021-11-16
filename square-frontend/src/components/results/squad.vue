<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div>
    <div class="row mb-4">
      <div class="col" v-html="currentContext" />
    </div>
    <div class="row">
      <div class="col">
        <div class="list-group list-group-flush">
          <a
              v-for="(res, index) in skillResult.results"
              :key="index"
              v-on:mouseover="setActive(index, res.prediction_documents[0].span)"
              class="list-group-item list-group-item-action"
              :class="{ active: index === activeResult }"
              :aria-current="index === activeResult"
              style="cursor: pointer">
            <div class="d-flex w-100 justify-content-between">
              <h5 class="mb-1">{{ index + 1 }}. Answer</h5>
              <span class="badge bg-primary p-2">{{ roundScore(res.prediction_score) }}%</span>
            </div>
            <small class="mb-1">{{ res.prediction_output.output }}</small>
            <div class="progress mt-2">
              <div
                  class="progress-bar progress-bar-striped bg-primary"
                  role="progressbar"
                  :style="{ width: `${roundScore(res.prediction_score)}%` }"
                  :aria-valuenow="roundScore(res.prediction_score)"
                  aria-valuemin="0"
                  aria-valuemax="100" />
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('squad', {
  props: ['skillResult'],
  mixins: [mixin],
  data() {
    return {
      activeResult: null,
      span: null
    }
  },
  computed: {
    currentContext: function () {
      return this.highlightSpan(this.$store.state.currentContext, this.span)
    }
  },
  methods: {
    setActive(index, span) {
      this.activeResult = index
      this.span = span
    }
  }
})
</script>
