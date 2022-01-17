<!-- Component for the Search Query. The user can enter a question here and change the query options. -->
<template>
  <div class="card border-primary shadow">
    <div class="card-body p-4">
      <Alert v-if="showEmptyWarning" class="alert-warning" dismissible>You need to enter a question!</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
      <form v-on:submit.prevent="askQuestion">
        <div class="row">
          <div class="col-xl">
            <div class="row">
              <div class="col">
                <div class="input-group">
                  <div class="form-floating flex-grow-1">
                    <textarea
                        v-model="currentQuestion"
                        @keydown.enter.exact.prevent
                        @keyup.enter.exact="askQuestion"
                        class="form-control rounded-0 overflow-hidden"
                        style="resize: none; white-space: nowrap; border-top-left-radius: 0.25rem !important"
                        id="question"
                        placeholder="Enter your question" />
                    <label for="question">Enter your question</label>
                  </div>
                  <button
                      class="btn btn-lg btn-primary rounded-0 d-inline-flex align-items-center"
                      style="border-top-right-radius: 0.25rem !important"
                      type="submit"
                      :disabled="waitingQuery">
                    <span v-show="waitingQuery" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                    &nbsp;Ask your question
                  </button>
                </div>
                <div class="form-floating mb-2">
                  <textarea
                      v-model="inputContext"
                      class="form-control rounded-0 rounded-bottom border-top-0"
                      style="resize: none"
                      :style="{ height: inputContextHeight + 'px'}"
                      id="context"
                      placeholder="Context seperated by line breaks (Optional)" />
                  <label for="context">Context seperated by line breaks (Optional)</label>
                </div>
                <small class="text-muted">Some skills require context.</small>
              </div>
            </div>
          </div>
          <div class="col-xl mt-3 mt-xl-0">
            <div class="row">
              <div class="col">
                <label for="skillSelect" class="form-label fs-5">Skill selector</label>
                <select v-model="options.selectedSkills" size="5" class="form-select" multiple id="skillSelect">
                  <option v-for="skill in availableSkills" v-bind:value="skill.id" v-bind:key="skill.id">
                    {{ skill.name }} — {{ skill.description }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'

export default Vue.component('query-skills', {
  data() {
    return {
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
  components: {
    Alert
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    },
    queryOptions() {
      return this.$store.state.queryOptions
    },
    currentQuestion: {
      get: function () {
        return this.inputQuestion
      },
      set: function (newValue) {
        let tmp = newValue.trimEnd().split('\n')
        this.inputQuestion = tmp.splice(0, 1)[0]
        if (tmp.length > 0) {
          this.inputContext = tmp.join('\n')
        }
      }
    },
    inputContextHeight() {
      return 58 + (this.inputContext ? 21 * 7 : 0)
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
        }).then(() => {
          this.failure = false
          this.failureMessage = ''
        }).catch(error => {
          this.failure = true
          this.failureMessage = error.data.msg
        }).finally(() => {
          this.waitingQuery = false
        })
      } else {
        this.showEmptyWarning = true
      }
    }
  },
  /**
   * Make the store update the skills and init the query options
   */
  beforeMount() {
    this.$store.dispatch('updateSkills')
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
