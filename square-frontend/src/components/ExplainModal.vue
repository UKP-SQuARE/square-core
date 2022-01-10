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
  mixins: [mixin]
})
</script>
