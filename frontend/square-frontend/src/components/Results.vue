<template>
  <b-container>
    <hr>
    <b-tabs>
      <b-tab v-for="skillResult in currentResults" v-bind:key="skillResult.name" v-bind:title="skillResult.name">
        <b-card class="mt-2" v-show="skillResult.error">
          <b-card-text>Error: {{ skillResult.error }}</b-card-text>
        </b-card>
        <b-card v-for="(res, i) in skillResult.results" v-bind:key="skillResult.name+i" class="mt-2">
          <component :is="res.type" v-bind:result="res"></component>
        </b-card>
      </b-tab>
    </b-tabs>
    
  </b-container>
</template>

<script>
import PlainText from '@/components/result/PlainText.vue'
import KeyValue from '@/components/result/KeyValue.vue'
export default {
  name: 'results',
  components: {
    "plain_text": PlainText,
    "key_value": KeyValue
  },
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
