<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div v-if="this.currentResults.length" class="card shadow p-3 mt-3">
    <nav>
      <div class="nav nav-tabs justify-content-center mt-3" id="skill-tab" role="tablist">
        <button
            v-for="(skillResult, index) in this.currentResults"
            :key="skillResult.name"
            class="nav-link"
            :class="{ 'active': activeTab === index }"
            :id="`skill-${skillResult.name}-tab`"
            data-bs-toggle="tab"
            :data-bs-target="`#skill-${skillResult.name}`"
            type="button"
            role="tab"
            v-on:click="activeTab = index">{{ skillResult.name }}</button>
      </div>
    </nav>
    <div class="card-body">
        <div class="tab-content" id="skill-tabContent">
          <div
              v-for="(skillResult, index) in this.currentResults"
              :key="skillResult.name"
              class="tab-pane fade"
              :class="{ 'show': activeTab === index, 'active': activeTab === index }"
              :id="`#skill-${skillResult.name}`">
            <Alert v-if="skillResult.error" class="alert-danger" dismissible>There was a problem: {{ skillResult.error }}</Alert>
            <component :is="skillResult.name.replace('-', '')" :skillResult="skillResult" />
          </div>
        </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'
import boolq from '@/components/results/boolq.vue'

export default Vue.component('results', {
  data() {
    return {
      activeTab: 0
    }
  },
  components: {
    Alert,
    boolq,
  },
  computed: {
    currentQuestion() {
      return this.$store.state.currentQuestion
    },
    currentResults() {
      return this.$store.state.currentResults.slice(0).sort((a, b) => {
        if (a['score'] < b['score']) {
          return 1
        } else if(a['score'] === b['score']) {
          return 0
        } else if(a['score'] > b['score']) {
          return -1
        }
      })
    }
  },
  methods: {
    highlight(text, span) {
      return span ? `${text.substring(0, span[0])}<span class="highlightText">${text.substring(span[0], span[1])}</span>${text.substring(span[1], text.length)}` : text
    }
  }
})
</script>
