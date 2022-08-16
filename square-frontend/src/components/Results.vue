<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div v-if="currentResults.length">
    <div class="row">
      <div class="col table-responsive bg-light border border-primary rounded shadow p-3 mx-3 mt-4">
        <table class="table table-borderless">
          <thead class="border-bottom border-dark">
          <tr>
<!--            This for name of the skills   eg: SQuAD 1.1 BERT Adapter-->
            <th v-if="skillType.options.name !== 'categorical-results'" scope="col" />
            <th
                v-for="(skillResult, index) in currentResults"
                :key="index"
                scope="col"
                class="fs-2 fw-light text-center">{{ skillResult.skill.name }}</th>
          </tr>
          <tr>
<!--            This is for type of model eg:Extractive QA, bert-base-uncased
 -->
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
    <div class="row">
      <div class="col mt-3" v-if="showContextToggle">
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

      <div class="col mt-3" v-if="explainAvailable">
        <div class="d-grid gap-2 d-md-flex justify-content-md-center">
          <a data-bs-toggle="modal" data-bs-target="#modalExplain" role="button" class="btn btn-primary shadow">
            Explain this output
          </a>
          <ExplainOutput id="modalExplain"/>
        </div>
      </div>

      <div class="col mt-3" v-if="this.$store.state.currentSkills.includes('62eb8f7765872e7b65ea5c8b')">
        <div class="d-grid gap-2 d-md-flex justify-content-md-center">
          <a data-bs-toggle="modal" data-bs-target="#modalGraph" role="button" class="btn btn-primary shadow">
            Show Graph
          </a>
          <GraphViz id="modalGraph"/>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Categorical from '@/components/results/Categorical.vue'
import SpanExtraction from '@/components/results/SpanExtraction.vue'
import ExplainOutput from '../components/modals/ExplainOutput'
import GraphViz from '../components/modals/GraphViz'

export default Vue.component('skill-results', {
  data() {
    return {
      showWithContext: false
    }
  },
  provide() {
    return {
      currentResults: this.$store.state.currentResults
    }
  },
  components: {
    Categorical,
    SpanExtraction,
    ExplainOutput,
    GraphViz
  },
  computed: {
    currentResults() {
      return this.$store.state.currentResults
    },
    skillType() {
      switch (this.$store.state.currentResults[0].skill.skill_type) {
        case 'abstractive':
          // Fall through
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
    },
    explainAvailable() {
      let skillTypeStr = this.$store.state.currentResults[0].skill.skill_type
      if (this.$store.state.currentSkills.includes('62eb8f7765872e7b65ea5c8b')) {
        return false;
      } else if (skillTypeStr === 'span-extraction' || skillTypeStr === 'multiple-choice') {
        return true
      } else {
        return false
      }
    }
  }
})
</script>
