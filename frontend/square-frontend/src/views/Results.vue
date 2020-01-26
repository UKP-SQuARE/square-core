<template>
  <b-container>
    <h2 class="text-center">{{currentQuestion}}</h2>
    <hr>
    <b-tabs>
      <b-tab v-for="skillResult in currentResults" v-bind:key="skillResult.skillName" v-bind:title="skillResult.skillName">
        <b-card v-for="(res, i) in skillResult.results" v-bind:key="skillResult.skillName+i" class="mt-2">
          <b-card-text>{{ res }}</b-card-text>
        </b-card>
      </b-tab>
    </b-tabs>
    
  </b-container>
</template>

<script>
export default {
  name: 'results',
  computed: {
    currentQuestion() {
      return this.$store.state.currentQuestion
    },
    currentResults() {
      return this.$store.state.currentResults
    }
  }
}
</script>
