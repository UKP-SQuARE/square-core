<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div v-if="currentResults.length" class="card border-primary shadow mt-3">
    <div class="card-header">
      <ul class="nav nav-tabs card-header-tabs justify-content-center">
        <li
            v-for="(skillResult, index) in currentResults"
            :key="skillResult.name"
            class="nav-item">
          <a class="nav-link h5 fw-light"
             :class="{ 'active': activeTab === index }"
             :id="`skill-${skillResult.name}-tab`"
             data-bs-toggle="tab"
             :data-bs-target="`#skill-${skillResult.name}`"
             v-on:click="activeTab = index">{{ skillResult.name }}</a>
        </li>
      </ul>
    </div>
    <div class="card-body p-4">
      <p class="lead text-center my-3">{{ currentQuestion }}</p>
      <div class="tab-content" id="skill-tabContent">
        <div
            v-for="(skillResult, index) in currentResults"
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
import commonsenseqa from '@/components/results/commonsenseqa.vue'
import squad from '@/components/results/squad.vue'

export default Vue.component('skill-results', {
  data() {
    return {
      activeTab: 0
    }
  },
  components: {
    Alert,
    boolq,
    commonsenseqa,
    squad
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
  }
})
</script>
