<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div v-if="currentResults.length">
    <div class="row">
      <div class="col table-responsive bg-light border border-primary rounded shadow p-3 mx-3">
        <table class="table table-borderless">
          <thead class="border-bottom border-dark">
          <tr>
            <th v-if="skillType.options.name !== 'categorical-results'" scope="col" />
            <th
                v-for="(skillResult, index) in currentResults"
                :key="index"
                scope="col"
                class="fs-2 fw-light text-center">{{ skillResult.skill.name }}</th>
          </tr>
          <tr>
            <th v-if="skillType.options.name !== 'categorical-results'" scope="col" />
            <th
                v-for="(skillResult, index) in currentResults"
                :key="index"
                scope="col"
                class="fw-normal text-center">{{ skillResult.skill.description }}</th>
          </tr>
          </thead>
          <tbody>
          <tr
              v-for="row in currentResults[0].predictions.length"
              :key="row">
            <th v-if="skillType.options.name !== 'categorical-results'" scope="row" class="pt-4 text-primary text-end">
              {{ row }}.
            </th>
            <component
                v-for="(skillResult, index) in currentResults"
                :key="index"
                :is="skillType"
                :prediction="skillResult.predictions[row - 1]"
                :showWithContext="showWithContext"
                :width="`${100 / currentResults.length }%`"
                style="min-width: 320px;"/>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="showContextToggle" class="row">
      <div class="col mt-3">
        <div class="d-grid gap-2 d-md-flex justify-content-md-center">
          <a
              v-on:click="showWithContext = !showWithContext"
              :class="{ 'active': showWithContext }"
              role="button"
              class="btn btn-primary shadow">
            Show answers {{ showWithContext ? 'without' : 'with' }} context
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Categorical from '@/components/results/Categorical.vue'
import SpanExtraction from '@/components/results/SpanExtraction.vue'

export default Vue.component('skill-results', {
  data() {
    return {
      showWithContext: false
    }
  },
  components: {
    Categorical,
    SpanExtraction
  },
  computed: {
    currentResults() {
      return this.$store.state.currentResults
    },
    skillType() {
      switch (this.$store.state.currentResults[0].skill.skill_type) {
        case 'span-extraction':
          // Fall through
        case 'multiple-choice':
          // Use span extraction without the span highlighting
          return SpanExtraction
        case 'categorical':
          return Categorical
        default:
            return null
      }
    },
    showContextToggle() {
      return this.$store.state.currentResults[0].skill.skill_type === 'span-extraction'
    }
  }
})
</script>
