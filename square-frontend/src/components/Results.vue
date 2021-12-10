<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <div v-if="currentResults.length" class="card border-primary shadow mt-3">
    <div class="card-header">
      <ul class="nav nav-tabs card-header-tabs justify-content-center">
        <li
            v-for="(skillResult, index) in currentResults"
            :key="skillResult.skill.name"
            class="nav-item">
          <a class="nav-link h5 fw-light"
             :class="{ 'active': activeTab === index }"
             :id="`skill-${skillResult.skill.name}-tab`"
             data-bs-toggle="tab"
             :data-bs-target="`#skill-${skillResult.skill.name}`"
             v-on:click="activeTab = index">{{ skillResult.skill.name }}</a>
        </li>
      </ul>
    </div>
    <div class="card-body p-4">
      <p class="lead text-center my-3">{{ currentQuestion }}</p>
      <div class="tab-content" id="skill-tabContent">
        <div
            v-for="(skillResult, index) in currentResults"
            :key="skillResult.skill.name"
            class="tab-pane fade"
            :class="{ 'show': activeTab === index, 'active': activeTab === index }"
            :id="`#skill-${skillResult.skill.name}`">
          <Alert v-if="skillResult.error" class="alert-danger" dismissible>There was a problem: {{ skillResult.error }}</Alert>
          <component :is="skillResult.skill.skill_type.replace('-', '')" :skillResult="skillResult" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'
import categorical from '@/components/results/categorical.vue'
import multiplechoice from '@/components/results/multiplechoice.vue'
import spanextraction from '@/components/results/spanextraction.vue'

export default Vue.component('skill-results', {
  data() {
    return {
      activeTab: 0
    }
  },
  components: {
    Alert,
    categorical,
    multiplechoice,
    spanextraction
  },
  computed: {
    currentQuestion() {
      return this.$store.state.currentQuestion
    },
    currentResults() {
      return this.$store.state.currentResults
    }
  }
})
</script>
