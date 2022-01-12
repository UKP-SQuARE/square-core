<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
        </div>
        <div class="modal-body">
          <div class="text-center">
            <h3 class="card-title mb-3">{{ test.test_name }}</h3>
            <p class="d-inline-flex align-items-center">
              <span class="badge bg-primary d-inline-flex align-items-center me-2 py-2">{{ mapTestType(test.test_type) }}</span>
              test on
              <span class="badge bg-primary d-inline-flex align-items-center ms-2 py-2">{{ test.capability }}</span>
            </p>
            <p>
              Failure rate <sup class="text-danger">{{ test.failed_cases }}</sup>&frasl;<sub>{{ test.total_cases }}</sub> = <strong class="text-danger">{{ roundScore(test.failed_cases / test.total_cases, false) }}%</strong>
            </p>
            <div class="progress flex-grow-1 align-self-center mx-2" title="Failure rate">
              <div
                  class="progress-bar bg-danger"
                  role="progressbar"
                  :style="{ width: `${roundScore(test.failed_cases / test.total_cases, false)}%` }"
                  :aria-valuenow="roundScore(test.failed_cases / test.total_cases, false)"
                  aria-valuemin="0"
                  aria-valuemax="100">
                {{ test.failed_cases }}
              </div>
              <div
                  class="progress-bar bg-success"
                  role="progressbar"
                  :style="{ width: `${roundScore(test.success_cases / test.total_cases, false)}%` }"
                  :aria-valuenow="roundScore(test.success_cases / test.total_cases, false)"
                  aria-valuemin="0"
                  aria-valuemax="100">
                {{ test.success_cases }}
              </div>
            </div>
          </div>
          <div class="container-fluid p-0">
            <h4 class="my-3">Failed Examples</h4>
            <ul class="list-group">
              <li class="list-group-item bg-light"
                  v-for="(test_case, index) in test.test_cases.slice(0, 5)"
                  :key="index">
                <div class="row">
                  <div class="col">
                    <strong>Question:</strong> <span v-html="applyChanges(test_case.question, test_case)" />
                  </div>
                </div>
                <div class="row my-3">
                  <div class="col">
                    <strong>Context:</strong> <span v-html="applyChanges(test_case.context, test_case)" />
                  </div>
                </div>
                <div class="row my-3">
                  <div class="col">
                    <strong class="text-success">Answer:</strong> <span v-if="'original_answer' in test_case && test_case.answer !== test_case.original_answer" v-html="replaceWithHighlights(`[${test_case.original_answer}->${test_case.answer}]`) " /><span v-else>{{ test_case.answer }} </span>
                    <span class="text-success d-inline-flex align-items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                        <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                      </svg>
                    </span>
                  </div>
                </div>
                <div class="row my-3">
                  <div class="col">
                    <strong class="text-danger">Prediction:</strong> {{ test_case.prediction }}
                    <span class="text-danger d-inline-flex align-items-center">
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
          <div class="text-center mt-3">
            Showing {{ Math.min(5, test.test_cases.length) }} out of {{ test.test_cases.length }} failed examples. Download all examples to see more.
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('explain-card', {
  props: ['test'],
  mixins: [mixin],
  methods: {
    prepareRegExp(token) {
      return new RegExp('([^\\w])' + token + '([^\\w])', 'ig')
    },
    applyChanges(value, test_case) {
      if ('changed' in test_case) {
        if ('where' in test_case && test_case[test_case.where] !== value) {
          // Skip changes if they are not universal and not included in the `where` field
          return value
        } else if (Array.isArray(test_case.changed.from)) {
          // Multiple replacements
          test_case.changed.from.forEach((from, index) => {
            let re = this.prepareRegExp(test_case.changed.to[index])
            value = value.replaceAll(re, `$1[${from}->${test_case.changed.to[index]}]$2`)
          })
        } else {
          // Single replacement
          let re = this.prepareRegExp(test_case.changed.to)
          value = value.replaceAll(re, `$1[${test_case.changed.from}->${test_case.changed.to}]$2`)
        }
        return this.replaceWithHighlights(value)
      } else if ('span' in test_case && test_case.context === value) {
        let span = value.substring(test_case.span[0], test_case.span[1])
        return value.replace(span, `<mark class="bg-success text-light">${span}</mark>`)
      }
      return value
    },
    replaceWithHighlights(value) {
      return value.replaceAll(/\[([^\]]*)->([^[]*)\]/ig, '<mark class="bg-warning">$1</mark><span class="d-inline-flex align-items-center px-1"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H4.5z"/></svg></span><mark class="bg-success text-light">$2</mark>')
    }
  }
})
</script>
