<template>
  <div>
    <form v-on:submit.prevent="showCheckList">
      <div class="row">
        <div class="col">
          <CompareSkills
              v-on:input="changeSelectedSkills"
              class="border-success"
              :skill-filter="skillId => skillId in data" />
        </div>
      </div>
      <div v-if="selectedSkills.length > 0" class="row">
        <div class="col my-3">
          <div class="d-grid gap-2 d-md-flex justify-content-md-center">
            <button type="submit" class="btn btn-success btn-lg shadow text-white" :disabled="waiting">
              <span v-show="waiting" class="spinner-border spinner-border-sm" role="status" />
              &nbsp;Show CheckList</button>
          </div>
        </div>
      </div>
    </form>
    <div v-if="currentTests.length > 0">
      <div class="row">
        <div class="col table-responsive bg-light border border-primary rounded shadow p-3 mx-3">
          <table class="table table-borderless">
            <thead class="border-bottom border-dark">
            <tr>
              <th
                  v-for="(skill, index) in currentSkills"
                  :key="index"
                  scope="col"
                  class="fs-2 fw-light text-center">{{ skill.name }}</th>
            </tr>
            <tr>
              <th
                  v-for="index in currentSkills.length"
                  :key="index"
                  scope="col"
                  class="fw-normal text-center">
                <a
                    v-on:click="downloadExamples(index)"
                    :ref="`downloadButton${index}`"
                    class="btn btn-outline-secondary d-inline-flex align-items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                    <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                    <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                  </svg>
                  &nbsp;Download all examples
                </a>
              </th>
            </tr>
            <tr>
              <th
                  v-for="(skill, index) in currentSkills"
                  :key="index"
                  scope="col"
                  class="fw-normal text-center">{{ skill.description }}</th>
            </tr>
            </thead>
            <tbody>
            <tr
                v-for="row in currentTests[0].length"
                :key="row">
              <td
                  v-for="index in currentSkills.length"
                  :key="index"
                  :width="`${100 / currentSkills.length }%`"
                  style="min-width: 320px;">
                <div class="progress flex-grow-1 align-self-center m-2" title="Failure rate">
                  <div
                      class="progress-bar bg-danger"
                      role="progressbar"
                      :style="{ width: `${roundScore(getTest(index, row).failed_cases / getTest(index, row).total_cases)}%` }"
                      :aria-valuenow="roundScore(getTest(index, row).failed_cases / getTest(index, row).total_cases)"
                      aria-valuemin="0"
                      aria-valuemax="100">{{ getTest(index, row).failed_cases }}</div>
                  <div
                      class="progress-bar bg-success"
                      role="progressbar"
                      :style="{ width: `${roundScore(getTest(index, row).success_cases / getTest(index, row).total_cases)}%` }"
                      :aria-valuenow="roundScore(getTest(index, row).success_cases / getTest(index, row).total_cases)"
                      aria-valuemin="0"
                      aria-valuemax="100">{{ getTest(index, row).success_cases }}</div>
                </div>
                <div class="text-center">
                  <h3 class="my-3">{{ getTest(index, row).test_name }}</h3>
                  <p class="d-inline-flex align-items-center">
                    <span class="badge bg-primary d-inline-flex align-items-center me-2 py-2">{{ mapTestType(getTest(index, row).test_type) }}</span>
                    test on
                    <span class="badge bg-primary d-inline-flex align-items-center ms-2 py-2">{{ getTest(index, row).capability }}</span>
                  </p>
                  <div>
                  <a
                      class="btn btn-outline-secondary d-inline-flex align-items-center"
                      data-bs-toggle="modal"
                      :data-bs-target="`#modal-${index}-${row}`"
                      role="button">
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-arrows-angle-expand" viewBox="0 0 16 16">
                      <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707z"/>
                    </svg>
                    &nbsp;Expand
                  </a>
                    </div>
                </div>
                <ExplainDetail :id="`modal-${index}-${row}`" :test="getTest(index, row)" />
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else class="row">
      <div class="col-md-8 mx-auto mt-4 text-center">
        <div class="bg-light border rounded shadow p-5 text-center">
          <div class="feature-icon bg-success bg-gradient">
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
            </svg>
          </div>
          <h2 class="display-5">Explainability</h2>
          <p class="lead fs-2">Test the <span class="text-success">behaviour</span> of <span class="text-success">black-box</span> models.</p>
          <p class="lead fs-2">Explore capabilities such as the <span class="text-success">robustness</span> of model output.</p>
          <p class="lead fs-2"><span class="text-success">Get started</span> by selecting up to three skills.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import CompareSkills from '../components/CompareSkills'
import ExplainDetail from '../components/modals/ExplainDetail'
import mixin from '../components/results/mixin'
import { getSkill } from '../api'
import squad2 from '../../checklist/61a9f57935adbbf1f2433073'
import boolq from '../../checklist/61a9f66935adbbf1f2433077'
import commonsense from '../../checklist/61a9f6d035adbbf1f243307d'

export default Vue.component('explainability-page', {
  mixins: [mixin],
  data() {
    return {
      waiting: false,
      options: {
        selectedSkills: []
      },
      currentSkills: [],
      currentTests: [],
      selectedTest: -1,
      data: {
        '61a9f57935adbbf1f2433073': squad2,
        '61a9f66935adbbf1f2433077': boolq,
        '61a9f6d035adbbf1f243307d': commonsense
      }
    }
  },
  components: {
    ExplainDetail,
    CompareSkills
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    },
    selectedSkills() {
      return this.options.selectedSkills.filter(skill => skill !== 'None')
    }
  },
  methods: {
    changeSelectedSkills(options, skillSettings) {
      skillSettings
      this.options = options
    },
    showCheckList() {
      this.waiting = true
      let currentSkills = []
      let currentTests = []
      this.selectedSkills.forEach(skill => {
        if (skill in this.data) {
          getSkill(skill)
              .then((response) => {
                currentSkills.push(response.data)
              })
          let tests = this.data[skill].tests
          // FIXME: Sort all tests the same
          tests.sort((a, b) => b.failure_rate - a.failure_rate)
          tests.forEach(test => test.test_cases = test.test_cases.filter(
              test_case => test_case['success_failed'] === 'failed'))
          currentTests.push(tests)
        }
      })
      this.currentSkills = currentSkills
      this.currentTests = currentTests
      this.waiting = false
    },
    getTest(skillIndex, testIndex) {
      return this.currentTests[skillIndex - 1][testIndex - 1]
    },
    downloadExamples(skillIndex) {
      let skill = this.currentSkills[skillIndex - 1]
      let data = JSON.stringify(this.data[skill.id], null, 2)
      let blob = new Blob([data], {type: 'application/json;charset=utf-8'})
      // FIXME: Does not download
      this.$refs[`downloadButton${skillIndex}`].href = URL.createObjectURL(blob)
      this.$refs[`downloadButton${skillIndex}`].download = `${skill.name} ${new Date().toLocaleString().replaceAll(/[\\/:]/g, '-')}.json`
    }
  }
})
</script>