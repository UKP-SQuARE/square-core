<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <form v-on:submit.prevent="onSubmit">
    <Card :title="originalName ? originalName : 'New skill'">
      <template #leftItem>
        <router-link to="/skills" class="btn btn-outline-primary d-inline-flex align-items-center" role="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-left-square" viewBox="0 0 16 16">
            <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
            <path d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z"/>
          </svg>
          &nbsp;My skills
        </router-link>
      </template>
      <template #rightItem>
        <button class="btn btn-outline-primary d-inline-flex align-items-center" type="submit">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-save" viewBox="0 0 16 16">
            <path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z"/>
          </svg>
          &nbsp;Save
        </button>
      </template>
      <Alert v-if="success" class="alert-success" dismissible>Skill was updated successfully.</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
      <div class="row">
        <div class="col-md-6 mt-3">
          <div class="form-floating">
            <input v-model="skill.name" type="text" class="form-control rounded-0 rounded-top" id="name" placeholder="Skill name">
            <label for="name">Skill name</label>
          </div>
        </div>
        <div class="col-md-6 mt-3">
          <div class="form-floating">
            <select v-model="skill.skill_type" class="form-select" id="skillType">
              <option v-for="skillType in skillTypes" v-bind:value="skillType" v-bind:key="skillType">
                {{ skillType }}
              </option>
            </select>
            <label for="skillType">Skill type</label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <div class="form-floating">
            <input v-model="skill.description" type="text" class="form-control rounded-0 rounded-top" id="description" placeholder="Description">
            <label for="description">Description</label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mt-3">
          <div class="form-floating">
            <input v-model="skill.skill_settings.requires_multiple_choices" type="number" class="form-control" id="maxResultsSkill" required>
            <label for="maxResultsSkill">Min multiple choice options</label>
          </div>
        </div>
        <div class="col-md-6 mt-3 d-flex align-items-center">
          <div class="form-check">
            <input v-model="skill.skill_settings.requires_context" v-bind:value="skill.skill_settings.requires_context" class="form-check-input" type="checkbox" id="flexCheckDefault">
            <label class="form-check-label" for="flexCheckDefault">
              Requires context
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <Status :url="skill.url" class="mb-2" />
          <div class="form-floating">
            <input v-model="skill.url" type="url" class="form-control rounded-0 rounded-top" id="url" placeholder="URL">
            <label for="url">URL</label>
            <small class="text-muted"><span class="text-info">scheme</span>://<span class="text-info">host</span>:<span class="text-info">port</span>/<span class="text-info">base_path</span></small>
          </div>
        </div>
      </div>
    </Card>
  </form>
</template>


<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'
import Card from '@/components/Card.vue'
import Status from '@/components/Status.vue'
import { getSkill, getSkillTypes } from '@/api'

export default Vue.component('edit-skill', {
  data() {
    return {
      skillTypes: [],
      skill: {
        name: '',
        skill_type: '',
        description: '',
        skill_settings: {
          requires_context: false,
          requires_multiple_choices: 0
        },
        url: '',
        default_skill_args : null,
        user_id: '',
        published: false,
        skill_input_examples: null
      },
      /**
       * The name for the title.
       * We do not use skill.name for this so that the title is only changed when the user updates the skill.
       */
      originalName: '',
      success: false,
      failure: false,
      failureMessage: ''
    }
  },
  components: {
    Alert,
    Card,
    Status
  },
  computed: {
    /**
     * Decides if we want to create a new skill or edit an existing skill
     */
    isCreateSkill() {
      return this.$route.params.id === 'new_skill'
    }
  },
  methods: {
    onSubmit() {
      if (this.isCreateSkill) {
        this.createSkill()
      } else {
        this.updateSkill()
      }
    },
    updateSkill() {
      this.success = false
      this.$store
          .dispatch('updateSkill', { skill: this.skill })
          .then(() => {
            this.originalName = this.skill.name
            this.success = true
            this.failure = false
          })
          .then(() => {
            this.$store.commit('initQueryOptions', { forceSkillInit: true })
          })
          .catch(failureMessage => {
            this.failure = true
            this.failureMessage = failureMessage
          })
    },
    createSkill() {
      this.$store
          .dispatch('createSkill', { skill: this.skill })
          .then(() => this.$router.push('/skills'))
          .catch(error => {
            this.failure = true
            this.failureMessage = error.data.msg
          })
    }
  },
  beforeMount() {
    getSkillTypes()
        .then((response) => {
          this.skillTypes = response.data
        })
    if (!this.isCreateSkill) {
      getSkill(this.$route.params.id)
          .then((response) => {
            this.skill = response.data
            this.originalName = this.skill.name
          })
    }
    this.skill.user_id = this.$store.state.user.name
  }
})
</script>
