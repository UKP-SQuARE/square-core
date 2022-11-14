<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <form v-on:submit.prevent="onSubmit">
    <Card :title="originalName ? originalName : 'New skill'">
      <template #leftItem>
        <router-link to="/skills" class="btn btn-outline-danger d-inline-flex align-items-center" role="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-caret-left-square" viewBox="0 0 16 16">
            <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
            <path d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z"/>
          </svg>
          &nbsp;My skills
        </router-link>
      </template>
      <template #rightItem>
        <button class="btn btn-outline-danger d-inline-flex align-items-center" type="submit">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-save" viewBox="0 0 16 16">
            <path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z"/>
          </svg>
          &nbsp;Save
        </button>
      </template>
      <Alert v-if="success" class="alert-success" dismissible>Skill was updated successfully.</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>An error occurred</Alert>
      <div class="row">
        <div class="col-md-6 mt-3">
          <label for="name" class="form-label">Skill name</label>
          <input v-model="skill.name" type="text" class="form-control" id="name" placeholder="Skill name">
        </div>
        <div class="col-md-6 mt-3">
          <label for="skillType" class="form-label">Skill type</label>
            <select v-model="skill.skill_type" class="form-select" id="skillType">
              <option v-for="skillType in skillTypes" v-bind:value="skillType" v-bind:key="skillType">
                {{ skillType }}
              </option>             
            </select>
        </div>
      </div>
      
      <div class="row">
        <div class="col-6 mt-3 d-flex align-items-center">
          <div class="form-check">
            <input v-model="skill.skill_settings.requires_context" v-bind:value="skill.skill_settings.requires_context" class="form-check-input" type="checkbox" id="requiresContext"
            v-on:change="SetSkillURL()">
            <label class="form-check-label d-inline-flex align-items-center" for="requiresContext">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-card-text" viewBox="0 0 16 16">
                <path d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h13zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z"/>
                <path d="M3 5.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 8a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 8zm0 2.5a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5z"/>
              </svg>
              &nbsp;Requires context
            </label>
          </div>
        </div>
        <div class="col-6 mt-3 d-flex align-items-center">
          <div class="form-check">
            <input v-model="skill.published" v-bind:value="skill.published" class="form-check-input" type="checkbox" id="published">
            <label class="form-check-label d-inline-flex align-items-center" for="published">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-globe" viewBox="0 0 16 16">
                <path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z"/>
              </svg>
              &nbsp;Public
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <label for="url" class="form-label">Skill URL</label>
            <input v-model="skill.url" type="url" class="form-control" id="url" placeholder="Skill URL">
            <small class="text-muted">URL to the hosted skill (<span class="text-info">scheme</span>://<span class="text-info">host</span>:<span class="text-info">port</span>/<span class="text-info">base_path</span>)</small>
            <div class="mt-2"><Status :url="skill.url" /></div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <label for="args" class="form-label">Skill arguments</label>
          <input v-model="skillArguments" type="text" class="form-control" :class="{ 'is-invalid': !validJSON }" id="args" placeholder="Skill argument as JSON">
          <div v-if="!validJSON" class="invalid-feedback">
            JSON is invalid
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col mt-3">
          <label for="datasets" class="form-label">Skill Datasets</label>
          <multiselect v-model="skill.data_sets" :options="dataSets" :multiple="true" :close-on-select="false" placeholder="Select a dataset"></multiselect>
          <small class="text-muted">Select one or more datasets that your skill should automatically be evaluated on.</small>
        </div>
      </div>
      <div class="row">
        <div class="col mt-4">
          <h3>Provide example questions</h3>
          <p class="mb-1">These examples will be featured alongside your skill.</p>
        </div>
      </div>
      <div v-for="(example, index) in skill.skill_input_examples" v-bind:key="index" class="row">
        <h4 class="mt-3">Example {{ index + 1 }}</h4>
        <div class="col-md mt-2">
          <label :for="`question${index}`" class="form-label">Question</label>
          <textarea
              v-model="example.query"
              class="form-control mb-2"
              style="resize: none;"
              :style="{ 'height': `${38 * (skill.skill_settings.requires_context ? 3 : 1)}px` }"
              :id="`question${index}`"
              placeholder="Question" />
        </div>
        <div v-if="skill.skill_settings.requires_context" class="col-md mt-2">
          <label :for="`context${index}`" class="form-label">Context</label>
          <textarea
              v-model="example.context"
              class="form-control mb-2"
              style="resize: none; height: calc(38px * 3);"
              :id="`context${index}`"
              placeholder="Context" />
        </div>

        <div v-if="skill.skill_type=='multiple-choice'" class="col-md mt-2">
          <label for="choices_loop" class="form-label">Write at least 2 answer choices.</label>
          <div class="row g-0" v-for="(choice, choice_idx) in list_answer_choices[index]" :key="choice_idx" id="choices_loop">
            <div class="col-sm">
              <div class="input-group input-group-sm mb-3">
                <span class="input-group-text" id="basic-addon1">{{choice_idx+1}}</span>
                <input v-model="list_answer_choices[index][choice_idx]" type="text" class="form-control form-control-sm">
              </div>
            </div>
          </div>
          <!-- button to add one more element to list_choices -->
          <div class="form-inline">
            <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addChoice(index)">Add Choice</button>
            <!-- button to remove one element of list_choices -->
            <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeChoice(index)">Remove Choice</button>
          </div>
        </div>
      </div>
    </Card>
  </form>
</template>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'
import Card from '@/components/Card.vue'
import Status from '@/components/Status.vue'
import { getSkill, getSkillTypes, getDataSets } from '@/api'

export default Vue.component('edit-skill', {
  data() {
    return {
      skillTypes: [],
      dataSets: [],
      skill: {
        name: '',
        skill_type: '',
        data_sets: [],
        description: '',
        skill_settings: {
          requires_context: false,
          requires_multiple_choices: 0
        },
        url: '',
        default_skill_args: null,
        user_id: '',
        published: false,
        skill_input_examples: []
      },
      /**
       * The name for the title.
       * We do not use skill.name for this so that the title is only changed when the user updates the skill.
       */
      originalName: '',
      success: false,
      failure: false,
      stringifiedJSON: '',
      validJSON: true,
      numberSkillExamples: 3,
      list_answer_choices: [["", ""], ["", ""], ["", ""]]
    }
  },
  components: {
    Alert,
    Card,
    Status,
    Multiselect
  },
  computed: {
    /**
     * Decides if we want to create a new skill or edit an existing skill
     */
    isCreateSkill() {
      return this.$route.params.id === 'new_skill'
    },
    skillArguments: {
      // Use intermediate stringified variable to not interrupt the users typing
      get: function () {
        return this.stringifiedJSON
      },
      set: function (newValue) {
        this.stringifiedJSON = newValue
        try {
          if (newValue.length > 0) {
            this.skill.default_skill_args = JSON.parse(newValue)
          } else {
            this.skill.default_skill_args = null
          }
          this.validJSON = true
        } catch (e) {
          this.validJSON = false
        }
      }
    },
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
      // if skill type is multiple-choice, add the list_answer_choices to the skill_input_examples
      if (this.skill.skill_type == 'multiple-choice') {
        for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
          this.skill.skill_input_examples[i]['choices'] = this.list_answer_choices[i]
        }
      }
      this.$store
          .dispatch('updateSkill', { skill: this.skill })
          .then(() => {
            this.originalName = this.skill.name
            this.success = true
            this.failure = false
          })
          .catch(() => {
            this.failure = true
          })
    },
    createSkill() {
      // if skill type is multiple-choice, add the list_answer_choices to the skill_input_examples
      if (this.skill.skill_type == 'multiple-choice') {
        for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
          this.skill.skill_input_examples[i]['choices'] = this.list_answer_choices[i]
        }
      }
      this.$store
          .dispatch('createSkill', { skill: this.skill })
          .then(() => this.$router.push('/skills'))
          .catch(() => {
            this.failure = true
          })
    },
    addInputExampleFields() {
      // Dynamically add input fields
      // In case the default amount is modified later this will adapt for legacy skills
      while (this.skill.skill_input_examples.length < this.numberSkillExamples) {
        this.skill.skill_input_examples.push({ 'query': '', 'context': '' })
      }
    },
    SetSkillURL() {
      if(this.skill.skill_type=='span-extraction') {
        this.skill.skill_settings.requires_context ? this.skill.url = 'http://extractive-qa' : this.skill.url = 'http://open-extractive-qa'
      }
    },
    addChoice(index) {
      this.list_answer_choices[index].push("")
    },
    removeChoice(index) {
      if (this.list_answer_choices[index].length > 2) {
        this.list_answer_choices[index].pop()
      } else {
        alert("You must have at least 2 choices.")
      }
    }
  },
  watch: {
    'skill.skill_type'(){
      switch(this.skill.skill_type){
        case 'abstractive':
          this.skill.url = 'http://generative-qa'
          break
        case 'span-extraction':
          if(this.skill.skill_settings.requires_context){
            this.skill.url = 'http://extractive-qa'
          }
          else{
            this.skill.url = 'http://open-extractive-qa'
          }
          break
        case 'multiple-choice':
          this.skill.url = 'http://multiple-choice-qa'
          break
        case 'categorical':
          this.skill.url = 'http://multiple-choice-qa'
          break
        case 'information-retrieval':
          this.skill.url = 'http://information-retrieval'
          break
        default:
          // 
          break
      }
    }
  },
  beforeMount() {
    getSkillTypes(this.$store.getters.authenticationHeader())
        .then((response) => {
          this.skillTypes = response.data
        })
    getDataSets(this.$store.getters.authenticationHeader())
        .then((response) => {
          this.dataSets = response.data
        })
    if (!this.isCreateSkill) {
      getSkill(this.$store.getters.authenticationHeader(), this.$route.params.id)
          .then((response) => {
            let data = response.data
            if (data.skill_input_examples == null) {
              data.skill_input_examples = []
            }
            this.skill = data
            this.originalName = this.skill.name
            // Trigger setter
            this.skillArguments = JSON.stringify(this.skill.default_skill_args)
            this.addInputExampleFields()
            if (this.skill.skill_input_examples[0].choices !== null){
              // for each skill_input_example, add the choices to the list_answer_choices
              for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
                this.list_answer_choices[i] = this.skill.skill_input_examples[i]['choices']
              }
              if (this.list_answer_choices.length < this.numberSkillExamples) {
                for (let i = this.list_answer_choices.length; i < this.numberSkillExamples; i++) {
                  this.list_answer_choices.push(["", ""])
                }
              }
            }
            // for the transition period between old format of answer choices and the new one
            if (this.skill.skill_input_examples[0].choices == null && this.skill.skill_type == 'multiple-choice') {
              this.list_answer_choices = [["", ""], ["", ""], ["", ""]]
            }
            
          })
    } else {
      this.addInputExampleFields()
    }
    this.skill.user_id = this.$store.state.userInfo.preferred_username
  }
})
</script>
