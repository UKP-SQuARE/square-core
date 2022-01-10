<!-- The Explainability Page. Contains information about this project -->
<template>
  <div>
    <div class="card border-primary shadow">
      <div class="card-body p-4">
        <form v-on:submit.prevent="onSubmit">
          <div class="row">
            <div class="col-lg">
              <div class="row">
                <div class="col">
                  <div class="input-group">
                    <div class="form-floating flex-grow-1">
                      <select v-model="options.selectedSkill" class="form-select rounded-0 rounded-start" id="skillSelect">
                        <option v-for="skill in availableSkills" v-bind:value="skill.id" v-bind:key="skill.id">
                          {{ skill.name }} — {{ skill.description }}
                        </option>
                      </select>
                      <label for="skillSelect" class="form-label col-form-label-sm text-muted">Skill selector</label>
                    </div>
                    <button
                        class="btn btn-lg btn-primary d-inline-flex align-items-center"
                        :class="`btn-${availableTestData ? 'primary' : 'secondary'}`"
                        type="submit"
                        :disabled="waiting || !availableTestData">
                      <span v-show="waiting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                      &nbsp;<span v-if="availableTestData">Show Checklist</span>
                      <span v-else>Not yet available</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
      <div v-if="tests.length > 0" class="card-footer bg-white p-3">
        <h5 class="card-title">{{ this.skill.name }}</h5>
        <p class="card-text">We show up to 5 failed test cases for each of the tests below. You can download all examples, including successful ones, as a JSON file.</p>
        <a v-on:click="downloadExamples" ref="downloadButton" class="btn btn-outline-secondary d-inline-flex align-items-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
          </svg>
          &nbsp;Download all examples
        </a>
      </div>
    </div>
    <div v-if="tests.length > 0" class="card-columns">
      <Card
          v-for="(test, index) in tests"
          :key="index"
          class="d-inline-block w-100">
        <template #topItem>
          <div class="progress flex-grow-1 align-self-center mx-2" title="Failure rate">
            <div
                class="progress-bar bg-danger"
                role="progressbar"
                :style="{ width: `${roundScore(test.failed_cases / test.total_cases)}%` }"
                :aria-valuenow="roundScore(test.failed_cases / test.total_cases)"
                aria-valuemin="0"
                aria-valuemax="100">
              {{ test.failed_cases }}
            </div>
            <div
                class="progress-bar bg-success"
                role="progressbar"
                :style="{ width: `${roundScore(test.success_cases / test.total_cases)}%` }"
                :aria-valuenow="roundScore(test.success_cases / test.total_cases)"
                aria-valuemin="0"
                aria-valuemax="100">
              {{ test.success_cases }}
            </div>
          </div>
        </template>
        <template #rightItem>
          <a
              v-on:click="selectedTest = isActiveTest(index) ? -1 : index"
              class="btn btn-outline-secondary d-inline-flex align-items-center"
              role="button">
            <svg v-if="isActiveTest(index)" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrows-angle-contract" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M.172 15.828a.5.5 0 0 0 .707 0l4.096-4.096V14.5a.5.5 0 1 0 1 0v-3.975a.5.5 0 0 0-.5-.5H1.5a.5.5 0 0 0 0 1h2.768L.172 15.121a.5.5 0 0 0 0 .707zM15.828.172a.5.5 0 0 0-.707 0l-4.096 4.096V1.5a.5.5 0 1 0-1 0v3.975a.5.5 0 0 0 .5.5H14.5a.5.5 0 0 0 0-1h-2.768L15.828.879a.5.5 0 0 0 0-.707z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrows-angle-expand" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707z"/>
            </svg>
          </a>
        </template>
        <div class="text-center">
          <h3 class="card-title mb-3">{{ test.test_name }}</h3>
          <p class="d-inline-flex align-items-center">
            <span class="badge bg-primary d-inline-flex align-items-center me-1 py-2">{{ mapTestType(test.test_type) }}</span>
            Test on
            <span class="badge bg-primary d-inline-flex align-items-center ms-1 py-2">{{ test.capability }}</span>
          </p>
          <p v-if="isActiveTest(index)">
            Failures <sup class="text-danger">{{ test.failed_cases }}</sup>&frasl;<sub>{{ test.total_cases }}</sub> = <strong class="text-danger">{{ roundScore(test.failed_cases / test.total_cases) }}%</strong>
          </p>
        </div>
        <div v-if="isActiveTest(index)" class="container-fluid p-0">
          <h4 class="my-3">Failed Examples</h4>
              <ul class="list-group">
                <li class="list-group-item bg-light"
                    v-for="(test_case, index) in test.test_cases.slice(0, 5)"
                    :key="index">
                  <div class="row">
                    <div class="col">
                      <strong>Question:</strong> {{ test_case.question }}
                    </div>
                  </div>
                  <div class="row my-3">
                    <div class="col">
                      <strong>Context:</strong> {{ test_case.context }}
                    </div>
                  </div>
                  <div class="row my-3">
                    <div class="col-6">
                      <strong class="text-success">Answer:</strong> {{ test_case.answer }}
                      <span class="text-success">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                              <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                            </svg>
                          </span>
                    </div>
                    <div class="col-6">
                      <strong class="text-danger">Prediction:</strong> {{ test_case.prediction }}
                      <span class="text-danger">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
                              <path fill-rule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
                              <path fill-rule="evenodd" d="M2.146 2.146a.5.5 0 0 0 0 .708l11 11a.5.5 0 0 0 .708-.708l-11-11a.5.5 0 0 0-.708 0Z"/>
                            </svg>
                          </span>
                    </div>
                  </div>
                </li>
              </ul>
        </div>
        <template v-if="isActiveTest(index)" #footer>
          <div class="card-footer text-center">
            Showing {{ Math.min(5, test.test_cases.length) }} out of {{ test.test_cases.length }} failed examples. Download all examples to see more.
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Card from '@/components/Card.vue'
import { getSkill } from '@/api'
import squad2 from '../../checklist/61a9f57935adbbf1f2433073.json'

export default Vue.component('explainability-page', {
  data() {
    return {
      waiting: false,
      options: {
        selectedSkill: ''
      },
      data: {
        '61a9f57935adbbf1f2433073': squad2
      },
      skill: {},
      tests: [],
      selectedTest: -1
    }
  },
  components: {
    Card
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    },
    availableTestData() {
      return this.options.selectedSkill in this.data
    }
  },
  methods: {
    onSubmit() {
      if (this.options.selectedSkill in this.data) {
        getSkill(this.options.selectedSkill)
            .then((response) => {
              this.skill = response.data
            })
        let tests = this.data[this.options.selectedSkill].tests
        tests.sort((a, b) => b.failure_rate - a.failure_rate)
        tests.forEach(test => test.test_cases = test.test_cases.filter(
            test_case => test_case['success_failed'] === 'failed'))
        this.tests = tests
      }
    },
    roundScore(score) {
      return Math.round(score * 1_000) / 10
    },
    downloadExamples() {
      let data = JSON.stringify(this.checklist_data, null, 2)
      let blob = new Blob([data], {type: 'application/json;charset=utf-8'})
      this.$refs.downloadButton.href = URL.createObjectURL(blob)
      this.$refs.downloadButton.download = `${this.skill.name} ${new Date().toLocaleString().replaceAll(/[\\/:]/g, '-')}.json`
    },
    isActiveTest(index) {
      return index === this.selectedTest
    },
    mapTestType(shorthand) {
      let map = {
        'MFT': 'Min Func Test',
        'INV': 'INVariance',
        'DIR': 'DIRectional'
      }
      if (shorthand in map) {
        return map[shorthand]
      } else {
        return shorthand
      }
    },
    highlightReplacement: function (source, target, doc) {
      return doc.replaceAll(target, `<mark class="bg-warning">${source}</mark><span class="d-inline-flex align-items-center px-1">
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H4.5z"/>
</svg></span><mark class="bg-success text-light">${target}</mark>`)
    }
  },
  /**
   * Make the store update the skills and init the explain options
   */
  beforeMount() {
    this.$store.dispatch('updateSkills')
        .then(() => {
          this.$store.commit('initExplainOptions', {})
        })
        .then(() => {
          // Copy the object so we do not change the state before a query is issued
          this.options = JSON.parse(
              JSON.stringify(this.$store.state.explainOptions)
          )
        })
  }
})
</script>