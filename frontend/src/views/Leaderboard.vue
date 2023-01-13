<template>
  <div>
    <div>
      <div class="bg-light mt-3 mb-5 py-4 px-4">
        <h2>Leaderboard</h2>
        <p>Compare different skills and how they perform on different datasets.</p>
        <p>Missing some results? Start a new evaluation and results will appear on the leaderboard once the evaluation finishes.</p>
        <router-link class="btn btn-primary" to="/evaluation" exact-active-class="active">Start new evaluation</router-link>
      </div>
    </div>
    
    <div>
      <div class="row">
        <div class="col-sm-8 col-12 mb-3">
          <label for="dataset" class="form-label">Dataset</label>
          <multiselect id="dataset" v-model="dataset_name" :options="datasets" :disabled=isLoading placeholder="Select a dataset" @select="refreshLeaderboard"></multiselect>
        </div>
        <div class="col-sm-4 col-12 mb-3">
          <label for="dataset" class="form-label">Metric</label>
          <multiselect id="metric" v-model="metric_name" :options="metrics" :disabled=isLoading placeholder="Select a metric" @select="refreshLeaderboard"></multiselect>
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
            <router-link to="/evaluation" exact-active-class="active" class="text-reset">Click here to start one yourself</router-link>
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
              <span class="badge bg-secondary">{{ date_format(data.item.date) }}</span>
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

const base_fields = [
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
let private_field = {
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
      dataset_name: "squad",
      metric_name: "squad",
      datasets: [],
      metrics: ["squad", "squad_v2", "exact_match"],
      fields: base_fields,
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
        this.datasets = ["squad", "quoref", "commonsense_qa", "cosmos_qa"]
      })
    this.refreshLeaderboard()
  },
  destroyed() {
    window.removeEventListener("resize", this.handleResize)
  },
  methods: {
    handleResize() {  
      this.doStackTable = window.innerWidth < 500
      if (this.doStackTable) {
        private_field.label = "Private" 
      } else {
        private_field.label = "" 
      }
    },
    date_format(date_string) {
      return new Date(date_string).toLocaleDateString()
    },
    refreshLeaderboard() {
      setTimeout(function() {
        this.isLoading = true
        getLeaderboard(this.dataset_name, this.metric_name, this.$store.getters.authenticationHeader())
          .then((response) => {
            this.fields = this.get_fields(response.data)
            this.items = response.data
            this.isLoading = false
          })
      }.bind(this), 50)
    },
    get_fields(leaderboard_entries) {
      let fields = [...base_fields]
      if (leaderboard_entries.length > 0) {
        // add column to display private-indicator
        if (this.contains_private_entries(leaderboard_entries)) {
          fields.unshift(private_field)
        }
        // add a column for each value of the metric
        Object.keys(leaderboard_entries[0].result).forEach((key) => {
          fields.push({
            key: "result." + key,
            label: this.get_metric_value_label(key),
            sortable: true,
            class: "align-middle",
          })
        })
      }
      return fields
    },
    contains_private_entries(leaderboard_entries) {
      let private_entries = leaderboard_entries.filter( (entry) => {
        return entry.private === true
      })
      return private_entries.length > 0
    },
    get_metric_value_label(metric_value_name) {
      switch (metric_value_name) {
        case "exact_match":
        case "exact":
          return "EM";
        case "f1":
          return "F1";
        default:
          return metric_value_name;
      }
    },
    round(value) {
      return parseFloat(value).toFixed(3)
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