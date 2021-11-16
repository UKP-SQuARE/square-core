<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div>
    <div class="row">
      <div class="col-xl-6 col-md-5 mb-4 mb-md-0">
        <div class="border rounded bg-light p-4" v-html="currentContext" />
      </div>
      <div class="col-xl-6 col-md-7">
        <div class="list-group list-group-flush">
          <a
              v-for="(res, index) in skillResult.results"
              :key="index"
              v-on:mouseover="setActive(index, res.prediction_documents[0].span)"
              class="list-group-item list-group-item-action"
              :class="{ 'border-primary': index === activeResult }"
              :aria-current="index === activeResult"
              style="cursor: pointer">
            <div class="d-flex w-100 justify-content-between align-items-start">
              <div class="d-flex align-items-baseline">
                <h5
                    class="m-0"
                    :class="{ 'text-primary': index === activeResult }">{{ index + 1 }}.</h5>
                <small class="mx-2">{{ res.prediction_output.output }}</small>
              </div>
              <span class="badge bg-transparent text-dark border border-primary p-2">{{ roundScore(res.prediction_score) }}%</span>
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
