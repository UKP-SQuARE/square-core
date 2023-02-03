<template>
  <div>
    <div>
      <div class="bg-light mt-3 mb-5 py-4 px-4">
        <h2>Leaderboard</h2>
        <p>Compare different skills and how they perform on different datasets.</p>
        <p>Missing some results? Start a new evaluation and results will appear on the leaderboard once the evaluation finishes.</p>
        <router-link class="btn btn-primary" to="/evaluations" exact-active-class="active">Start new evaluation</router-link>
      </div>
    </div>
    
    <div>
      <div class="row">
        <div class="col-sm-8 col-12 mb-3">
          <label for="dataset" class="form-label">Dataset</label>
          <multiselect id="dataset" v-model="datasetName" :options="datasetNames" :disabled=isLoading placeholder="Select a dataset" @select="refreshLeaderboard('dataset')"></multiselect>
        </div>
        <div class="col-sm-4 col-12 mb-3">
          <label for="dataset" class="form-label">Metric</label>
          <multiselect id="metric" v-model="metricName" :options="metrics" :disabled=isLoading placeholder="Select a metric" @select="refreshLeaderboard('metric')"></multiselect>
        </div>
      </div>
      <b-table striped hover borderless show-empty :stacked="doStackTable" :busy="isLoading" :items="items" :fields="fields" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc">
        <template #table-busy>
          <div class="text-center text-secondary my-4">
            <b-spinner class="align-middle"></b-spinner>
            &nbsp;
            <strong>Retrieving leaderboard</strong>
          </div>
        </template>
        <template #empty>
          <div class="text-center text-secondary my-4">
            <strong>There are no evaluation results for the selected dataset and metric</strong>
            <br>
            <router-link to="/evaluations" exact-active-class="active" class="text-reset">Click here to start one yourself</router-link>
          </div>
        </template>
        <template #cell(private)="data">
          <div class="stacked">
            <span v-if="data.item.private">Yes</span>
            <span v-else>No</span>
          </div>
          <div v-if="data.item.private" class="lock-container position-absolute top-50 start-50 translate-middle">
            <span data-bs-toggle="tooltip" data-bs-placement="topright" title="Only you are able to see this results, because your skill is set to private." class="position-absolute top-50 start-50 translate-middle">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 1C8.676 1 6 3.676 6 7v1c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2V7c0-3.324-2.676-6-6-6zm0 2c2.276 0 4 1.724 4 4v1H8V7c0-2.276 1.724-4 4-4zm0 10c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"/></svg>
            </span>
          </div>
        </template>
        <template #cell(rank)="data">
          <div class="text-center d-flex">
            <div>
              <span>{{ data.value }}</span><br>
              <span class="badge bg-secondary">{{ dateFormat(data.item.date) }}</span>
            </div>
          </div>
        </template>
        <template #cell()="data">
          <span v-if="isNaN(data.value)">{{ data.value }}</span>
          <span v-else>{{ round(data.value) }}</span>
        </template>
      </b-table>
    </div>
  </div>
</template>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<script>
import Vue from "vue"
import Multiselect from 'vue-multiselect'
import { getLeaderboard, getDataSets } from '@/api'
import { BootstrapVue } from "bootstrap-vue"
import "bootstrap-vue/dist/bootstrap-vue.css"
Vue.use(BootstrapVue)

const baseFields = [
  {
    key: "rank",
    label: "Rank",
    sortable: true,
    class: "align-middle rank",
    isRowHeader: true
  },
  {
    key: "skill_name",
    label: "Skill",
    sortable: false,
    class: "align-middle"
  }
]
let privateField = {
  key: "private",
  label: "",
  sortable: false,
  class: "position-relative lock"
}

export default Vue.component("show-leaderboard", {
   data() {
    return {
      doStackTable: false,
      isLoading: false,
      sortBy: "rank",
      sortDesc: false,
      datasetName: "squad",
      metricName: null,
      datasets: [],
      metrics: ["squad", "squad_v2", "exact_match"],
      fields: baseFields,
      items: []
    }
  },
  components: {
    Multiselect
  },
  mounted() {
    this.handleResize()
    window.addEventListener("resize", this.handleResize)
    getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        this.datasets = response.data
        this.datasets = [
          {
            "name": "squad",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "context-column": "context",
              "answer-text-column": "answers.text"
            }
          }, {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "context-column": "context",
              "answer-text-column": "answers.text"
            }
          }, {
            "name": "commonsense_qa",
            "skill-type":" multiple-choice",
            "metric": "exact_match",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "choices-columns": ["choices.text"],
              "choices-key-mapping-column": "choices.label",
              "answer-index-column": "answerKey"
            }
          }, {
            "name": "cosmos_qa",
            "skill-type": "multiple-choice",
            "metric": "exact_match",
            "mapping":{
              "id-column": "id",
              "question-column": "question",
              "choices-columns": ["answer0", "answer1", "answer2", "answer3"],
              "choices-key-mapping-column": null,
              "answer-index-column": "label"
            }
          }
        ]
      })
    this.refreshLeaderboard()
  },
  destroyed() {
    window.removeEventListener("resize", this.handleResize)
  },
  computed: {
    datasetNames: function() {
      return this.datasets.map(dataset => dataset.name);
    }
  },
  methods: {
    handleResize() {  
      this.doStackTable = window.innerWidth < 500
      if (this.doStackTable) {
        privateField.label = "Private" 
      } else {
        privateField.label = "" 
      }
    },
    dateFormat(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    refreshLeaderboard(triggeredBy) {
      setTimeout(function() {
        this.isLoading = true
        if (triggeredBy != "metric") {
          let defaultMetric = this.getDefaultMetric(this.datasetName)
          this.metricName = defaultMetric || this.metricName
        }
        getLeaderboard(this.datasetName, this.metricName, this.$store.getters.authenticationHeader())
          .then((response) => {
            this.fields = this.getFields(response.data)
            this.items = response.data
            this.isLoading = false
          })
      }.bind(this), 50)
    },
    getFields(leaderboardEntries) {
      let fields = [...baseFields]
      if (leaderboardEntries.length > 0) {
        // add column to display private-indicator
        if (this.containsPrivateEntries(leaderboardEntries)) {
          fields.unshift(privateField)
        }
        // add a column for each value of the metric
        Object.keys(leaderboardEntries[0].result).forEach((key) => {
          fields.push({
            key: "result." + key,
            label: this.getMetricValueLabel(key),
            sortable: true,
            class: "align-middle",
          })
        })
      }
      return fields
    },
    containsPrivateEntries(leaderboardEntries) {
      let privateEntries = leaderboardEntries.filter( (entry) => {
        return entry.private === true
      })
      return privateEntries.length > 0
    },
    getMetricValueLabel(metricValueName) {
      switch (metricValueName) {
        case "exact_match":
        case "exact":
          return "EM";
        case "f1":
          return "F1";
        default:
          return metricValueName;
      }
    },
    round(value) {
      return parseFloat(value).toFixed(3)
    },
    getDefaultMetric(datasetName) {
      let dataset = this.datasets.filter(dataset => dataset.name === datasetName)
      if (!dataset.length) return null
      return dataset[0].metric ? dataset[0].metric : null
    }
  }
})
</script>

<style scoped>
::v-deep .sr-only{
  display:none !important
}

.lock svg {
  width: 100%;
  height: 100%;
  fill: var(--bs-secondary);
}
</style>

<style>
.table.b-table.b-table-stacked > tbody > tr > [data-label]::before {
  width: 25%;
  text-align: left;
  padding-right: 1em;
}

.table.b-table.b-table-stacked > tbody > tr > th > div > div {
  text-align: left !important;
  display: flex;
}

.table.b-table.b-table-stacked > tbody > tr > th > div > div > .badge {
  margin-left: 1em;
}

.stacked {
  display: block;
}

.lock-container {
  width: 100%;
  height: 100%;
  display: none;
}

@media (min-width: 500px) {
  th.align-middle.rank {
    width: 120px;
  }

  .lock {
    width: 30px;
  }

  .stacked {
    display: none;
  }

  .lock-container {
    display: block;
  }
}
</style>