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
              class="btn btn-outline-secondary d-inline-flex align-items-center"
              data-bs-toggle="modal"
              :data-bs-target="`#modal-${index}`"
              role="button">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrows-angle-expand" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707z"/>
            </svg>
          </a>
        </template>
        <div class="text-center">
          <h3 class="card-title mb-3">{{ test.test_name }}</h3>
          <p class="d-inline-flex align-items-center">
            <span class="badge bg-primary d-inline-flex align-items-center me-2 py-2">{{ mapTestType(test.test_type) }}</span>
            test on
            <span class="badge bg-primary d-inline-flex align-items-center ms-2 py-2">{{ test.capability }}</span>
          </p>
        </div>
        <ExplainModal :id="`modal-${index}`" :test="test" />
      </Card>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Card from '@/components/Card.vue'
import ExplainModal from '@/components/ExplainModal.vue'
import mixin from '@/components/results/mixin.vue'
import { getSkill } from '@/api'
import squad2 from '../../checklist/61a9f57935adbbf1f2433073.json'
import boolq from '../../checklist/61a9f66935adbbf1f2433077.json'

export default Vue.component('explainability-page', {
  mixins: [mixin],
  data() {
    return {
      waiting: false,
      options: {
        selectedSkill: ''
      },
      data: {
        '61a9f57935adbbf1f2433073': squad2,
        '61a9f66935adbbf1f2433077': boolq
      },
      skill: {},
      tests: [],
      selectedTest: -1
    }
  },
  components: {
    Card,
    ExplainModal
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
    downloadExamples() {
      let data = JSON.stringify(this.data[this.options.selectedSkill], null, 2)
      let blob = new Blob([data], {type: 'application/json;charset=utf-8'})
      this.$refs.downloadButton.href = URL.createObjectURL(blob)
      this.$refs.downloadButton.download = `${this.skill.name} ${new Date().toLocaleString().replaceAll(/[\\/:]/g, '-')}.json`
    },
    isActiveTest(index) {
      return index === this.selectedTest
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