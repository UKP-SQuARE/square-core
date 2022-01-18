<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <Query />
    <Results v-if="isShowingResults" />
    <div v-else class="col-lg-6 mx-auto mt-5 p-5 bg-light border rounded-3">
      <h2 class="d-inline-flex align-items-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-lightbulb" viewBox="0 0 16 16">
          <path d="M2 6a6 6 0 1 1 10.174 4.31c-.203.196-.359.4-.453.619l-.762 1.769A.5.5 0 0 1 10.5 13a.5.5 0 0 1 0 1 .5.5 0 0 1 0 1l-.224.447a1 1 0 0 1-.894.553H6.618a1 1 0 0 1-.894-.553L5.5 15a.5.5 0 0 1 0-1 .5.5 0 0 1 0-1 .5.5 0 0 1-.46-.302l-.761-1.77a1.964 1.964 0 0 0-.453-.618A5.984 5.984 0 0 1 2 6zm6-5a5 5 0 0 0-3.479 8.592c.263.254.514.564.676.941L5.83 12h4.342l.632-1.467c.162-.377.413-.687.676-.941A5 5 0 0 0 8 1z"/>
        </svg>
        &nbsp;Question Answering
      </h2>
      <p>Try questions on extractive, multiple choice, and categorical skills.</p>
      <p>Open domain skills work without any context while multiple choice skills need to be presented with more than one line of options.</p>
      <p>Select one or multiple skills to get started.</p>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Query from '@/components/Query.vue'
import Results from '@/components/Results.vue'

export default Vue.component('square-home', {
  components: {
    Query,
    Results
  },
  computed: {
    isShowingResults() {
      return this.$store.state.currentResults.length > 0
    }
  }
})
</script>