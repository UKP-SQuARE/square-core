<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <form v-on:submit.prevent="onSubmit">
    <Card title="New evaluation">
      <template #leftItem>
        <router-link to="/evaluations" class="btn btn-outline-danger d-inline-flex align-items-center" role="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor"
            class="bi bi-caret-left-square" viewBox="0 0 16 16">
            <path
              d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z" />
            <path
              d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z" />
          </svg>
          &nbsp;My evaluations
        </router-link>
      </template>
      <template #rightItem>
        <button class="btn btn-outline-danger d-inline-flex align-items-center" type="submit">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-save"
            viewBox="0 0 16 16">
            <path
              d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z" />
          </svg>
          &nbsp;Run evaluation
        </button>
      </template>
      <Alert v-if="success" class="alert-success" dismissible>Skill was updated successfully.</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>An error occurred</Alert>
      <div class="row">
        <div class="col mt-3">
          <label for="dataset" class="form-label">Skill</label>
          <multiselect id="dataset" v-model="skillName" :options="skills" placeholder="Select a skill"></multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <div class="form-check form-switch">
            <input v-model="showOnlyPrivateSkills" v-bind:value="showOnlyPrivateSkills" class="form-check-input" type="checkbox"
              role="switch" id="published">
            <label class="form-check-label d-inline-flex align-items-center" for="published">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-globe"
                viewBox="0 0 16 16">
                <path
                  d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z" />
              </svg>
              &nbsp; Private Skills &nbsp;
              <svg
                content="Select this if you want to see only private skills."
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <label for="dataset" class="form-label">Datasets</label>
          <multiselect id="dataset" v-model="datasetName" :options="dataSets" placeholder="Select a dataset"></multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <label for="dataset" class="form-label">Metrics</label>
          <multiselect id="dataset" v-model="metricName" :options="metrics" placeholder="Select a metric"></multiselect>
        </div>
      </div>
    </Card>
  </form>
</template>

<style src="vue-multiselect/dist/vue-multiselect.min.css">

</style>

<script>
import Vue from 'vue'

import Alert from '@/components/Alert.vue'
import Card from '@/components/Card.vue'
import { getSkills, runEvaluation, getDataSets } from '@/api'

import VueTippy from "vue-tippy";
Vue.use(VueTippy);

import Multiselect from 'vue-multiselect'



export default Vue.component('edit-skill', {
  data() {
    return {
      skills: [],
      dataSets: [],
      metrics: ["squad", "squad_v2", "exact_match"],
      skillsPublishedState: {},
      skillIDs: {},
      success: false,
      failure: false,
      skillName: null,
      datasetName: null,
      metricName: null,
      showOnlyPrivateSkills: false,
      header: null
    }
  },
  components: {
    Alert,
    Card,
    Multiselect
  },
  computed: {

  },
  methods: {
    onSubmit() {
      this.runEval()
    },
    runEval() {
      runEvaluation(this.$store.getters.authenticationHeader(), this.skillIDs[this.skillName], this.datasetName, this.metricName)
          .then(() => {
            this.success = true
            this.$router.push('/evaluations')
          })
          .catch(() => {
            this.failure = true
          })
    },
    updateSkills() {
      this.skills = []
      for (const [skill_name, skill_is_published] of Object.entries(this.skillsPublishedState)) {
        if(skill_is_published == false && this.showOnlyPrivateSkills == true) {
          this.skills.push(skill_name)
        }
        if(this.showOnlyPrivateSkills == false) {
          this.skills.push(skill_name)
        }
      }
    }

  },
  watch: {
    'showOnlyPrivateSkills'() {
        this.updateSkills()
      }
  },
  beforeMount() {
    getSkills(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let i = 0; i < response.data.length; i++) {
          this.skillsPublishedState[response.data[i].name] = response.data[i].published
          this.skillIDs[response.data[i].name] = response.data[i].id
          this.skills.push(response.data[i].name)
        }
      })
    getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let i = 0; i < response.data.length; i++) {
          this.dataSets.push(response.data[i].name)
        }
      })
  }
})
</script>

<style lang="css">
/* style the background and the text color of the input ... */

.vue-tags-input .ti-input {
  padding: 0px 0px;
  border: 0px;
}

.vue-tags-input .ti-tag {
  padding: 0px 5px;
}

.vue-tags-input .ti-new-tag-input-wrapper {
  margin: 0px;
}
</style>
