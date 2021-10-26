<!-- Component for the Search Query. The user can enter a question here and change the query options. -->
<template>
  <b-form v-on:submit.prevent="askQuestion">
    <b-alert v-model="showEmptyWarning" variant="danger" dismissible>You need to enter a question!</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>
    <b-tabs content-class="m-3" align="center">
      <b-tab title="Question" active>
        <b-input-group>
          <b-form-input v-model="inputQuestion" required placeholder="Enter your question" />
          <b-input-group-append>
            <b-button type="submit" variant="primary" :disabled="waitingQuery">
              Ask your question
              <b-spinner v-show="waitingQuery" small label="Spinning" />
            </b-button>
          </b-input-group-append>
        </b-input-group>
      </b-tab>
      <b-tab title="Context QA" lazy>
        <b-form-row>
          <b-col>
            <b-form-input
                v-model="inputQuestion"
                required
                placeholder="Enter your question"
                class="rounded-top"
                style="border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom-style: dashed" />
            <b-form-textarea
                v-model="inputContext"
                required
                placeholder="Provide context seperated by line breaks"
                rows="5"
                no-resize
                class="rounded-bottom border-top-0"
                style="border-top-left-radius: 0; border-top-right-radius: 0" />
          </b-col>
        </b-form-row>
        <b-form-row>
          <b-col class="text-right mt-3">
            <b-button type="submit" variant="primary" :disabled="waitingQuery">
              Ask your question
              <b-spinner v-show="waitingQuery" small label="Spinning" />
            </b-button>
          </b-col>
        </b-form-row>
      </b-tab>
    </b-tabs>
    <div class="m-3">
      <b-form-checkbox v-model="showOptions" switch>Show expert options</b-form-checkbox>
      <div class="mt-3" v-show="showOptions">
        <b-form-row>
          <b-form-group class="col" label="Skill Selector:" label-for="skill-selector">
            <b-form-select
                id="skill-selector"
                v-model="options.selector"
                :options="availableSkillSelectors"
            ></b-form-select>
          </b-form-group>
        </b-form-row>
        <b-form-row>
          <b-form-group class="col" label="Only use these skills:" label-for="skill-select">
            <b-form-select
                id="skill-select"
                v-model="options.selectedSkills"
                :options="availableSkills"
                multiple
                :select-size="Math.min(4, availableSkills.length)"
            ></b-form-select>
          </b-form-group>
        </b-form-row>
        <b-form-row>
          <b-form-group class="col-6" label="Maximum number of querried skills:" label-for="max-querried-skills">
            <b-form-input
                id="max-querried-skills"
                v-model="options.maxQuerriedSkills"
                required
                type="number"
            ></b-form-input>
          </b-form-group>
          <b-form-group class="col-6" label="Maximum number of results per skill:" label-for="max-results-skill">
            <b-form-input
                id="max-results-skill"
                v-model="options.maxResultsPerSkill"
                required
                type="number"
            ></b-form-input>
          </b-form-group>
        </b-form-row>
      </div>
    </div>
  </b-form>
</template>

<script>
import Vue from 'vue'

export default Vue.component('query', {
  data() {
    return {
      showOptions: false,
      waitingQuery: false,
      options: {
        selectedSkills: []
      },
      showEmptyWarning: false,
      inputQuestion: '',
      inputContext: '',
      failure: false,
      failureMessage: ''
    }
  },
  computed: {
    /**
     * Map state.availableSkills in the format for Vue Bootstrap
     */
    availableSkills() {
      return this.$store.state.availableSkills.map(skill => {
        return {
          text: `${skill.name} ${
              skill.description ? '- ' + skill.description : ''
          }`,
          value: skill
        }
      })
    },
    availableSkillSelectors() {
      return this.$store.state.availableSkillSelectors.map(selector => {
        return {
          text: `${selector.name} ${
              selector.description ? '- ' + selector.description : ''
          }`,
          value: selector.name
        }
      })
    },
    queryOptions() {
      return this.$store.state.queryOptions
    }
  },
  methods: {
    askQuestion() {
      if (this.inputQuestion.length > 0) {
        this.showEmptyWarning = false
        this.waitingQuery = true
        this.$store.dispatch('query', {
          question: this.inputQuestion,
          inputContext: this.inputContext,
          options: this.options
        }).catch(error => {
          this.failure = true
          this.failureMessage = error.data.msg
        }).finally(() => {
          this.waitingQuery = false
          // Collapse the options once results are here to save space. This is due to query and results residing in one view.
          this.showOptions = false
        })
      } else {
        this.showEmptyWarning = true
      }
    }
  },
  /**
   * Make the store update the skills and init the query options
   * Subscribe to mutation changes for the websocket
   */
  beforeMount() {
    var self = this
    this.$store.subscribe(mutation => {
      if (mutation.type === 'SOCKET_SKILLRESULT') {
        this.showOptions = false
        if (mutation.payload.error_msg) {
          self.failure = true
          self.failureMessage = mutation.payload.error_msg
          self.waitingQuery = false
        }
        if (mutation.payload.finished) {
          self.waitingQuery = false
        }
      }
    })
    this.$store.dispatch('updateSkills')
        .then(() => this.$store.dispatch('updateSelectors'))
        .then(() => {
          this.$store.commit('initQueryOptions', {})
        })
        .then(() => {
          // Copy the object so we do not change the state before a query is issued
          this.options = JSON.parse(
              JSON.stringify(this.$store.state.queryOptions)
          )
        })
  }
})
</script>
