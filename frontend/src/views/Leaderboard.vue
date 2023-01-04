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
      <b-table striped hover borderless :stacked="doStackTable" :busy="isLoading" :items="items" :fields="fields" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc">
        <template #table-busy>
          <div class="text-center text-secondary my-4">
            <b-spinner class="align-middle"></b-spinner>
            &nbsp;
            <strong>Retrieving leaderboard</strong>
          </div>
        </template>
        <template #cell(rank)="data">
          <div class="text-center">
            <span>{{ data.value }}</span><br>
            <span class="badge bg-secondary">{{ date_format(data.item.date) }}</span>
          </div>
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
    class: "align-middle test",
    isRowHeader: true
  },
  {
    key: "skill_name",
    label: "Skill",
    sortable: false,
    class: "align-middle"
  }
]

export default Vue.component("show-leaderboard", {
   data() {
    return {
      doStackTable: false,
      isLoading: false,
      sortBy: "rank",
      sortDesc: false,
      dataset_name: "quoref",
      metric_name: "squad",
      datasets: [],
      metrics: [],
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
      })
    this.refreshLeaderboard()
  },
  destroyed() {
    window.removeEventListener("resize", this.handleResize)
  },
  methods: {
    handleResize() {  
      this.doStackTable = window.innerWidth < 500
    },
    date_format(date_string) {
      return new Date(date_string).toLocaleDateString()
    },
    get_fields(items) {
      let fields = base_fields
      if (items.length > 0) {
        Object.keys(items[0].result).forEach((key) => {
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
    get_metric_value_label(metric_value_name) {
      switch (metric_value_name) {
        case "exact_match":
          return "EM";
        case "f1":
          return "F1";
        default:
          return metric_value_name;
      }
    },
    refreshLeaderboard() {
      this.isLoading = true
      getLeaderboard(this.dataset_name, this.metric_name, this.$store.getters.authenticationHeader())
        .then((response) => {
          this.fields = this.get_fields(response.data)
          this.items = response.data
          this.isLoading = false
        })
    }
  }
})
</script>

<style scoped>
::v-deep .sr-only{
  display:none !important
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

@media (min-width: 500px) {
  th.align-middle.test {
    width: 120px;
  }
}
</style>