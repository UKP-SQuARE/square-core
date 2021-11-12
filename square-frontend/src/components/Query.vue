<!-- Component for the Search Query. The user can enter a question here and change the query options. -->
<template>
  <div class="card border-primary shadow">
    <div class="card-header">
      <ul class="nav nav-tabs card-header-tabs justify-content-center">
        <li class="nav-item">
          <a class="nav-link active"
             id="nav-question-tab"
             data-bs-toggle="tab"
             data-bs-target="#nav-question"
             type="button"
             role="tab"
             aria-controls="nav-question"
             aria-selected="true">Question</a>
        </li>
        <li class="nav-item">
          <a class="nav-link"
             id="nav-context-tab"
             data-bs-toggle="tab"
             data-bs-target="#nav-context"
             type="button"
             role="tab"
             aria-controls="nav-context"
             aria-selected="true">Context QA</a>
        </li>
      </ul>
    </div>
    <div class="card-body p-4">
      <Alert v-if="showEmptyWarning" class="alert-warning" dismissible>You need to enter a question!</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
      <form v-on:submit.prevent="askQuestion">
        <div class="tab-content" id="nav-tabContent">
          <div class="tab-pane fade show active" id="nav-question" role="tabpanel" aria-labelledby="nav-question-tab">
            <div class="row mb-3">
              <div class="col">
                <div class="input-group">
                  <div class="form-floating flex-grow-1">
                    <input
                        v-model="inputQuestion"
                        type="text"
                        class="form-control rounded-0 rounded-start"
                        id="floatingQuestion"
                        placeholder="Enter your question"
                        aria-label="Enter your question">
                    <label for="floatingQuestion">Enter your question</label>
                  </div>
                  <button class="btn btn-outline-primary" type="submit" :disabled="waitingQuery">
                    <span v-show="waitingQuery" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                    Ask your question
                  </button>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <input type="checkbox" data-bs-toggle="collapse" data-bs-target="#collapseExample" class="btn-check" id="btn-check" autocomplete="off">
                <label class="btn btn-outline-secondary" for="btn-check">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-sliders" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M11.5 2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM9.05 3a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0V3h9.05zM4.5 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2.05 8a2.5 2.5 0 0 1 4.9 0H16v1H6.95a2.5 2.5 0 0 1-4.9 0H0V8h2.05zm9.45 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-2.45 1a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0v-1h9.05z"/>
                  </svg>
                  Show expert options
                </label>
              </div>
            </div>
          </div>
          <div class="tab-pane fade" id="nav-context" role="tabpanel" aria-labelledby="nav-context-tab">
            <div class="row mb-3">
              <div class="col">
                <div class="form-floating">
                  <textarea
                      v-model="currentQuestion"
                      class="form-control rounded-0 rounded-top"
                      placeholder="Enter your question"
                      id="floatingContextQuestion"
                      rows="1"
                      style="resize: none; white-space: nowrap; overflow: scroll" />
                  <label for="floatingContextQuestion">Enter your question</label>
                </div>
                <div class="form-floating">
                  <textarea
                      v-model="inputContext"
                      class="form-control rounded-0 rounded-bottom border-top-0"
                      placeholder="Context seperated by line breaks"
                      id="floatingContext"
                      style="height: 120px; resize: none" />
                  <label for="floatingContext">Context seperated by line breaks</label>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-6">
                <input type="checkbox" data-bs-toggle="collapse" data-bs-target="#collapseExample" class="btn-check" id="btn-check" autocomplete="off">
                <label class="btn btn-outline-secondary" for="btn-check">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-sliders" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M11.5 2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM9.05 3a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0V3h9.05zM4.5 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2.05 8a2.5 2.5 0 0 1 4.9 0H16v1H6.95a2.5 2.5 0 0 1-4.9 0H0V8h2.05zm9.45 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-2.45 1a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0v-1h9.05z"/>
                  </svg>
                  Show expert options
                </label>
              </div>
              <div class="col-6 text-end">
                <button class="btn btn-outline-primary" type="submit" :disabled="waitingQuery">
                  <span v-show="waitingQuery" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                  Ask your question
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="collapse" id="collapseExample">
          <div class="row mt-3">
            <div class="col">
              <div class="form-floating">
                <select v-model="options.selector" class="form-select" id="skillSelector">
                  <option v-for="skill in availableSkillSelectors" v-bind:value="skill.value" v-bind:key="skill.value">
                    {{ skill.text }}
                  </option>
                </select>
                <label for="skillSelector">Skill selector</label>
              </div>
            </div>
          </div>
          <div class="row mt-3">
            <div class="col">
              <label for="skillSelect" class="form-label col-form-label-sm text-muted">Only use these skills</label>
              <select v-model="options.selectedSkills" class="form-select" multiple id="skillSelect">
                <option v-for="skill in availableSkills" v-bind:value="skill.value" v-bind:key="skill.value">
                  {{ skill.text }}
                </option>
              </select>
            </div>
          </div>
          <div class="row mt-3">
            <div class="col-6">
              <div class="form-floating mb-3">
                <input v-model="options.maxQuerriedSkills" type="number" class="form-control" id="maxQuerriedSkills" required>
                <label for="maxQuerriedSkills">Max querried skills</label>
              </div>
            </div>
            <div class="col-6">
              <div class="form-floating mb-3">
                <input v-model="options.maxResultsPerSkill" type="number" class="form-control" id="maxResultsSkill" required>
                <label for="maxResultsSkill">Max results per skill</label>
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

export default Vue.component('query', {
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
    /**
     * Map state.availableSkills in the format for Vue Bootstrap
     */
    availableSkills() {
      return this.$store.state.availableSkills.map(skill => {
        return {
          text: `${skill.name} ${
              skill.description ? '- ' + skill.description : ''
          }`,
          value: skill.name
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
    let self = this
    this.$store.subscribe(mutation => {
      if (mutation.type === 'SOCKET_SKILLRESULT') {
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
