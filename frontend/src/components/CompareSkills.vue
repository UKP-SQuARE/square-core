<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">


        <div class="container text-center" style="height: 20em; overflow-y: scroll;">
          <div class="row">
            <div class="col col-3 d-none d-md-block">
              <div class="container text-start"></div>
              <div class="row">
                <div class="col text-start">
                  <h4>Tasks</h4>
                  <div v-for="skillType in skillTypes" :key="skillType" style="display:inline;">
                    <span role="button" v-on:click="addRemoveSkillTypeFilter(skillType)" :id="skillType"
                      class="btn btn-outline-primary btn-sm mb-1 me-1">
                      {{ skillType }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col text-start">
                  <h4>Domain</h4>
                  <span role="button" v-on:click="addRemoveScopeFilter('single_skill')" class="btn btn-outline-primary btn-sm me-1 mb-1" id="single_skill">
                    Single Domain</span>
                  <span role="button" v-on:click="addRemoveScopeFilter('multi_skill')" class="btn btn-outline-primary btn-sm me-1 mb-1" id="multi_skill">
                    Multi Domain</span>
                </div>
              </div>

              <div class="row">
                <div class="col text-start">
                  <h4>Datasets</h4>
                  <div v-for="dataset in availableDatasets" :key="dataset" style="display:inline;">
                    <span role="button" v-on:click="addRemoveDatasetFilter(dataset)" :id="dataset"
                      class="btn btn-outline-primary btn-sm  mb-1 me-1">
                      {{ dataset }}
                    </span>
                  </div>

                </div>
              </div>
            </div>
            <div class="col col-md-9">
              <!-- Search Bar -->
              <div class="input-group input-group-sm mb-2">
                <span class="input-group-text" id="basic-addon1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                    class="bi bi-search" viewBox="0 0 16 16">
                    <path
                      d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z">
                    </path>
                  </svg>
                </span>
                <input v-model="searchText" placeholder="Search skill" class="form-control form-control-xs" />
              </div>

              <!-- Skills -->
              <div class="row row-cols-1 row-cols-sm-2">
                <div class="col mb-2" v-for="(skill, index) in filteredSkills" :key="skill.id">
                  <div class="d-flex flex-wrap w-100 h-100">
                    <input class="btn-check" type="checkbox" v-on:input="selectSkill(skill.id, index)"
                      v-bind:value="skill.id"
                      :disabled="waiting || (selectedSkills.length >= 3 && !selectedSkills.includes(skill.id))"
                      :id="skill.id">
                    <label
                      class="btn btn-outline-primary d-flex align-middle align-items-center justify-content-center w-100 h-100"
                      :for="skill.id" :content=getSkillInfo(skill) v-tippy style="--bs-bg-opacity: 1">
                      <span class="text-break">{{ skill.name }}
                        <br>
                        <small class="text-muted">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                            class="bi bi-pencil-square" viewBox="0 0 16 16">
                            <path
                              d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z" />
                            <path fill-rule="evenodd"
                              d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z" />
                          </svg>
                          {{ skill.skill_type }}
                          <span class="px-1.5 text-gray-300">• </span>
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-aspect-ratio" viewBox="0 1 16 16">
                            <path d="M0 3.5A1.5 1.5 0 0 1 1.5 2h13A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 12.5v-9zM1.5 3a.5.5 0 0 0-.5.5v9a.5.5 0 0 0 .5.5h13a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-13z"/>
                            <path d="M2 4.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1H3v2.5a.5.5 0 0 1-1 0v-3zm12 7a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1 0-1H13V8.5a.5.5 0 0 1 1 0v3z"/>
                          </svg>
                          300M
                        </small>
                      </span>
                    </label>
                  </div>


                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import VueTippy from "vue-tippy";
Vue.use(VueTippy);

import { getDataSets, getSkillTypes } from '@/api'

export default Vue.component('compare-skills', {
  props: ['selectorTarget', 'skillFilter'],
  data() {
    return {
      searchText: '',
      waiting: false,
      chosenSkillType: null,
      selectedSkillScope: null,
      skillTypes: [],
      availableDatasets: [],
      selectedDatasets: [],
      options: {
        selectedSkills: []
      }

    }
  },
  computed: {
    filteredSkills() {
      let availableSkills = this.$store.state.availableSkills
      // Apply skill type filter
      if (this.chosenSkillType) {
        availableSkills = availableSkills.filter(skill => skill.skill_type == this.chosenSkillType)
      }
      // Apply search filter
      if (this.searchText) {
        availableSkills = availableSkills.filter((item) => this.searchText
          .toLowerCase()
          .split(" ")
          .every(v => item.name.toLowerCase().includes(v)))
      }
      // Apply selected datasets filer
      if (this.selectedDatasets.length > 0) {
        // for each selected dataset, filter available skills by dataset_id
        for (let dataset of this.selectedDatasets) {
          availableSkills = availableSkills.filter(skill => skill.data_sets.includes(dataset))
        }
      }
      // Apply filter based on selected skills
      // if at least one skill is selected
      if (this.options.selectedSkills.filter(skill => skill == 'None').length != 3) {
        availableSkills = availableSkills.filter(skill => skill.skill_type === this.skillSettings.skillType
          && skill.skill_settings.requires_context === this.skillSettings.requiresContext)
      }
      // Apply filter based on Skill Scope (single vs multi-skill)
      if (this.selectedSkillScope === 'single_skill') {
        availableSkills = availableSkills.filter(skill => skill.data_sets.length <= 1)
      } else if (this.selectedSkillScope === 'multi_skill') {
        availableSkills = availableSkills.filter(skill => skill.data_sets.length > 1)
      }
      return availableSkills
    },
    availableSkills() {
      let availableSkills = this.$store.state.availableSkills
      // Apply optional filter from props
      if (this.skillFilter !== undefined) {
        return availableSkills.filter(skill => this.skillFilter(skill.id))
      } else {
        return availableSkills
      }
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
      this.selectedSkills.forEach((skillId, index) => {
        this.availableSkills.forEach(skill => {
          if (skillId === skill.id) {
            if (index === 0) {
              settings.skillType = skill.skill_type
              settings.requiresContext = skill.skill_settings.requires_context
            } else if (skill.skill_type !== settings.skillType || skill.skill_settings.requires_context !== settings.requiresContext) {
              this.options.selectedSkills[index] = 'None'
            }
            // Require a minimum of 1 line if context is required else pick from the maximum of selected skills
            settings.requiresMultipleChoices = Math.max(
              settings.requiresContext ? 1 : 0,
              settings.requiresMultipleChoices,
              skill.skill_settings.requires_multiple_choices)
          }
        })
      })
      return settings
    }
  },
  methods: {
    minSkillsSelected(num) {
      return this.selectedSkills.length >= num
    },
    filterByTask(chosenSkillType) {
      this.skillSettings.skillType = chosenSkillType
      console.log(this.skillSettings.skillType)
    },
    addRemoveDatasetFilter(dataset) {
      if (this.selectedDatasets.includes(dataset)) {
        // remove dataset from selectedDatasets
        let index = this.selectedDatasets.indexOf(dataset)
        this.selectedDatasets.splice(index, 1)
        // remove active class to dataset button
        document.getElementById(dataset).classList.remove('active')
      } else {
        // add dataset to selectedDatasets
        this.selectedDatasets.push(dataset)
        // add active class to dataset button
        document.getElementById(dataset).classList.add('active')
      }
    },
    addRemoveSkillTypeFilter(skillType) {
      // remove all active classes from skill type buttons
      for (let type of this.skillTypes) {
        document.getElementById(type).classList.remove('active')
      }
      if (this.chosenSkillType === skillType) {
        this.chosenSkillType = null
      } else {
        this.chosenSkillType = skillType
        document.getElementById(skillType).classList.add('active')
      }
    },
    addRemoveScopeFilter(scope) {
      // remove all active classes from scope buttons
      for (let scope of ['single_skill', 'multi_skill']) {
        document.getElementById(scope).classList.remove('active')
      }
      if (this.selectedSkillScope === scope) {
        this.selectedSkillScope = null
      } else {
        this.selectedSkillScope = scope
        document.getElementById(scope).classList.add('active')
      }
    },
    selectSkill(skill_id) {
      if (this.options.selectedSkills.includes(skill_id)) {
        let index = this.options.selectedSkills.indexOf(skill_id)
        this.$set(this.options.selectedSkills, index, "None")
      }
      else {
        let index = this.options.selectedSkills.indexOf('None')
        this.$set(this.options.selectedSkills, index, skill_id)
      }
      this.$store.dispatch('selectSkill', { skillOptions: this.options, selectorTarget: this.selectorTarget })
      this.$emit('input', this.options, this.skillSettings)

    },
    skillBaseModel(skill) {
      // if skill.default_skill_args['base_model'] is not null
      if (skill.default_skill_args && skill.default_skill_args['base_model']) {
        return skill.default_skill_args['base_model']
      } else {
        return 'N/A'
      }
    },
    skillAdapter(skill) {
      // if skill.default_skill_args['adapter'] is not null
      if (skill.default_skill_args && skill.default_skill_args['adapter']) {
        return skill.default_skill_args['adapter']
      } else {
        return ''
      }
    },
    getSkillInfo(skill) {
      let skillInfo = ''
      if (skill.description !== '') {
        skillInfo += skill.description + '<br/>'
      }

      skillInfo += this.boxIcon() + ' HuggingFace\'s ID: ' + this.skillBaseModel(skill)
      
      if (this.skillAdapter(skill) !== '') {
        skillInfo += '<br/>' + this.boxIcon() + ' Adapter: ' + this.skillAdapter(skill)
      }
      return skillInfo
    },
    boxIcon(){
      return '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-seam" viewBox="0 0 16 16"> <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z" /></svg>'
    }

  },
  beforeMount() {
    this.waiting = true
    this.$store.dispatch('updateSkills')
      .then(() => {
        this.$store.state.skillOptions[this.selectorTarget].selectedSkills.forEach((skill, index) => {
          this.$set(this.options.selectedSkills, index, skill)
        })
        this.$emit('input', this.options, this.skillSettings)
      }).finally(() => {
        this.waiting = false
      })
    // get available datasets
    getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        this.availableDatasets = response.data
      })
      .catch((error) => {
        console.log(error)
      })
    // get skill types
    getSkillTypes(this.$store.getters.authenticationHeader())
      .then((response) => {
        this.skillTypes = response.data
      })
      .catch((error) => {
        console.log(error)
      })  
  },
})
</script>
