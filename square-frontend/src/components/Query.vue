<!-- Component for the Search Query. The user can enter a question here and change the query options. -->
<template>
  <form v-on:submit.prevent="askQuestion">
    <div class="row">
      <div class="col-md-4 ms-auto">
        <div class="bg-light border border-danger rounded shadow h-100 p-3">
          <div class="w-100">
            <div class="mb-3">
              <label for="skill1" class="form-label">1. Select a skill</label>
              <SkillSelector
                  v-model="options.selectedSkills[0]"
                  v-on:change-skills="changeSkills"
                  :skills="availableSkills"
                  id="skill1" />
            </div>
            <div class="mb-3">
              <label for="skill2" class="form-label">Compare up to three skills</label>
              <SkillSelector
                  v-model="options.selectedSkills[1]"
                  v-on:change-skills="changeSkills"
                  :skills="availableSkillsBasedOnSettings"
                  id="skill2"
                  :disabled="!minSkillsSelected(1)" />
            </div>
            <div class="mb-3">
              <SkillSelector
                  v-model="options.selectedSkills[2]"
                  v-on:change-skills="changeSkills"
                  :skills="availableSkillsBasedOnSettings"
                  id="skill3"
                  :disabled="!minSkillsSelected(2)" />
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4 me-auto mt-4 mt-md-0">
        <div class="bg-light border border-success rounded shadow h-100 p-3">
          <div class="w-100">
            <label for="question" class="form-label">2. Enter you question</label>
            <textarea
                v-model="currentQuestion"
                @keydown.enter.exact.prevent
                class="form-control form-control-lg mb-2"
                style="resize: none; height: calc(48px * 2.25);"
                id="question"
                placeholder="Question"
                required
                :disabled="!minSkillsSelected(1)" />
            <p v-if="currentExamples.length > 0" class="form-label">Or try one of these examples</p>
            <span
                role="button"
                v-for="(example, index) in currentExamples"
                :key="index"
                v-on:click="selectExample(example)"
                class="badge bg-success m-1 text-wrap lh-base">{{ example.query }}</span>
          </div>
        </div>
      </div>
      <div v-if="skillSettings.requiresContext" class="col-md-4 mt-4 mt-md-0">
        <div class="bg-light border border-warning rounded shadow h-100 p-3">
          <div class="w-100">
            <label for="context" class="form-label">3. Provide context</label>
            <textarea
                v-model="inputContext"
                class="form-control mb-2"
                style="resize: none; height: calc(38px * 7);"
                id="context"
                :placeholder="contextPlaceholder"
                required />
            <small class="text-muted">{{ contextHelp }}</small>
          </div>
        </div>
      </div>
    </div>
    <div v-if="minSkillsSelected(1)" class="row">
      <div class="col my-3">
        <div class="d-grid gap-2 d-md-block d-md-flex justify-content-md-center">
          <button
              type="submit"
              class="btn btn-danger btn-lg shadow text-white"
              :disabled="waitingQuery">
            <span v-show="waitingQuery" class="spinner-border spinner-border-sm" role="status" />
            &nbsp;Ask your question</button>
        </div>
      </div>
    </div>
  </form>
</template>

<script>
import Vue from 'vue'
import SkillSelector from '@/components/SkillSelector.vue'

export default Vue.component('query-skills', {
  data() {
    return {
      waitingQuery: false,
      options: {
        selectedSkills: []
      },
      inputQuestion: '',
      inputContext: '',
      failure: false,
      failureMessage: '',
      skillSettings: {
        skillType: null,
        requiresContext: false,
        requiresMultipleChoices: 0
      }
    }
  },
  components: {
    SkillSelector
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    },
    availableSkillsBasedOnSettings() {
      return this.availableSkills.filter(skill => skill.skill_type === this.skillSettings.skillType
          && skill.skill_settings.requires_context === this.skillSettings.requiresContext)
    },
    selectedSkills() {
      return this.options.selectedSkills.filter(skill => skill !== 'None')
    },
    currentQuestion: {
      get: function () {
        return this.inputQuestion
      },
      set: function (newValue) {
        let tmp = newValue.trimEnd().split('\n')
        this.inputQuestion = tmp.splice(0, 1)[0]
        if (tmp.length > 0) {
          this.inputContext = tmp.join('\n')
        }
      }
    },
    currentExamples() {
      // Pseudo random return 3 examples from currently selected skills
      return this.availableSkills
          .filter(skill => skill.skill_input_examples !== null
              && skill.skill_input_examples.length > 0
              && this.selectedSkills.includes(skill.id))
          .flatMap(skill => skill.skill_input_examples)
          .sort(() => 0.5 - Math.random())
          .slice(0, 3)
    },
    contextPlaceholder() {
      if (this.skillSettings.requiresMultipleChoices) {
        let choices = this.skillSettings.requiresMultipleChoices
        return `Provide ${choices > 1 ? choices + ' lines' : 'one line'} of context`
      } else {
        return 'No context required'
      }
    },
    contextHelp() {
      let help = 'no'
      if (this.skillSettings.requiresMultipleChoices) {
        let choices = this.skillSettings.requiresMultipleChoices
        help = `${choices > 1 ? choices + ' lines' : 'one line'} of`
      }
      return `Your selected skills require ${help} context.`
    }
  },
  methods: {
    minSkillsSelected(num) {
      return this.selectedSkills.length >= num
    },
    askQuestion() {
      this.waitingQuery = true
      this.$store.dispatch('query', {
        question: this.inputQuestion,
        inputContext: this.inputContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.options.maxResultsPerSkill
        }
      }).then(() => {
        this.failure = false
        this.failureMessage = ''
      }).catch(error => {
        this.failure = true
        this.failureMessage = error.data.msg
      }).finally(() => {
        this.waitingQuery = false
      })
    },
    changeSkills() {
      let settings = {
        skillType: null,
        requiresContext: false,
        requiresMultipleChoices: 0
      }
      this.availableSkills.forEach(skill => {
        if (this.selectedSkills.includes(skill.id)) {
          if (settings.skillType === null) {
            settings.skillType = skill.skill_type
          }
          settings.requiresContext = settings.requiresContext || skill.skill_settings.requires_context
          // Require a minimum of 1 line if context is required else pick from the maximum of selected skills
          settings.requiresMultipleChoices = Math.max(
              settings.requiresContext ? 1 : 0,
              settings.requiresMultipleChoices,
              skill.skill_settings.requires_multiple_choices)
        }
      })
      this.skillSettings = settings
    },
    selectExample(example) {
      this.inputQuestion = example.query
      if (this.skillSettings.requiresContext) {
        this.inputContext = example.context
      }
      this.askQuestion()
    }
  },
  /**
   * Make the store update the skills and init the query options
   */
  beforeMount() {
    this.$store.dispatch('updateSkills')
        .then(() => {
          // Copy the object so we do not change the state before a query is issued
          this.options = JSON.parse(
              JSON.stringify(this.$store.state.queryOptions)
          )
        })
  }
})
</script>
