<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">
        <label for="skill1" class="form-label d-block placeholder-glow">
          <span v-if="waiting" class="placeholder w-25" />
          <span v-else>1. Select a skill</span>
        </label>
        <SkillSelector
            v-model="options.selectedSkills[0]"
            v-on:input="selectSkill"
            :skills="availableSkills"
            id="skill1"
            :disabled="waiting" />
      </div>
      <div class="mb-3">
        <label for="skill2" class="form-label d-block placeholder-glow">
          <span v-if="waiting" class="placeholder w-50" />
          <span v-else>Compare up to three skills</span>
        </label>
        <SkillSelector
            v-model="options.selectedSkills[1]"
            v-on:input="selectSkill"
            :skills="availableSkillsBasedOnSettings"
            id="skill2"
            :disabled="!minSkillsSelected(1)" />
      </div>
      <div class="mb-3">
        <SkillSelector
            v-model="options.selectedSkills[2]"
            v-on:input="selectSkill"
            :skills="availableSkillsBasedOnSettings"
            id="skill3"
            :disabled="!minSkillsSelected(2)" />
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import SkillSelector from '@/components/SkillSelector.vue'

export default Vue.component('compare-skills', {
  props: ['selectorTarget', 'skillFilter'],
  data() {
    return {
      waiting: false,
      options: {
        selectedSkills: []
      }
    }
  },
  components: {
    SkillSelector
  },
  computed: {
    availableSkills() {
      let availableSkills = this.$store.state.availableSkills
      // Apply optional filter from props
      if (this.skillFilter !== undefined) {
        return availableSkills.filter(skill => this.skillFilter(skill.id))
      } else {
        return availableSkills
      }
    },
    availableSkillsBasedOnSettings() {
      return this.availableSkills.filter(skill => skill.skill_type === this.skillSettings.skillType
          && skill.skill_settings.requires_context === this.skillSettings.requiresContext)
    },
    selectedSkills() {
      return this.options.selectedSkills.filter(skill => skill !== 'None')
    },
    skillSettings() {
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
      return settings
    }
  },
  methods: {
    minSkillsSelected(num) {
      return this.selectedSkills.length >= num
    },
    selectSkill() {
      this.$store.dispatch('selectSkill', { skillOptions: this.options, selectorTarget: this.selectorTarget })
      this.$emit('input', this.options, this.skillSettings)
    }
  },
  beforeMount() {
    this.waiting = true
    this.$store.dispatch('updateSkills')
        .then(() => {
          // Copy the object so we do not change the state before a query is issued
          this.options = JSON.parse(JSON.stringify(this.$store.state.skillOptions[this.selectorTarget]))
          this.$emit('input', this.options, this.skillSettings)
        }).finally(() => {
          this.waiting = false
        })
  }
})
</script>
