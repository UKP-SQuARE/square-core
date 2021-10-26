<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
    <b-row v-if="currentResults.length" class="mt-4">
      <b-col>
        <b-tabs>
          <b-tab v-for="skillResult in currentResults" v-bind:key="skillResult.name">
            <template v-slot:title>
              {{ skillResult.name }} <small>{{ parseInt(skillResult.score * 100) }}% relevant</small>
            </template>
            <h6 class="text-muted mt-2 mb-1 ml-1">{{ skillResult["skill-description"] }}</h6>
            <b-card class="mt-2" v-show="skillResult.error">
              <b-card-text>Error: {{ skillResult.error }}</b-card-text>
            </b-card>
            <b-card
                v-for="(res, i) in skillResult.predictions"
                v-bind:key="res['prediction-documents'] + i"
                class="mt-2"
                header-bg-variant="primary"
                header-text-variant="white"
                footer-tag="footer">
              <template #header>
                <h6 class="mb-0">
                  <span style="float: left">{{ res["prediction-output"].output }}</span>
                  <span style="float: right">{{ res["prediction-output"]["output-score"] }}</span>
                </h6>
              </template>
              <b-card-text v-html="highlight(res['prediction-documents'][0].document, res['prediction-documents'][0].span)" />
              <component :is="res.type" v-bind:result="res" />
              <template #footer>
                <div>
                  <b-button v-b-toggle.collapse-2 class="mt-1">
                    See similar documents ({{ res['prediction-documents'].length - 1 }})
                  </b-button>
                  <b-collapse id="collapse-2" class="mt-2">
                    <b-card>I should start open!</b-card>
                  </b-collapse>
                </div>
              </template>
            </b-card>
          </b-tab>
        </b-tabs>
      </b-col>
    </b-row>
</template>

<script>
import Vue from 'vue'
import PlainText from '@/components/results/PlainText.vue'
import KeyValue from '@/components/results/KeyValue.vue'
import RawHTML from '@/components/results/HTML.vue'

export default Vue.component('results', {
  components: {
    // Be careful that the name does not overlap with an existing HTML component (e.g. text, html)
    PlainText,
    KeyValue,
    RawHTML
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
      return `${text.substring(0, span[0])}<span class="highlightText">${text.substring(span[0], span[1])}</span>${text.substring(span[1], text.length)}`
    }
  }
})
</script>
