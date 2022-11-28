<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">
          <div class="container">
            <div class="row align-items-center mb-2 ">
              <div class="col col-sm-4">
                <div class="input-group input-group-sm mb-2">
                  <span class="input-group-text" id="basic-addon1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                      <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"></path>
                    </svg>
                  </span>
                  <input v-model="searchText" placeholder="Search skill" class="form-control form-control-xs"/>
                </div>
              </div> <!-- end search col -->
              
              <div class="col-sm text-end">
                <label for="btn_group_task">Filter by task: &nbsp;</label>
                <div class="btn-group btn-group-sm flex-wrap" id="btn_group_task" role="group" aria-label="Filter by task">

                  <input type="radio" v-model="chosenSkillType" value="span-extraction" class="btn-check" name="btnradio" id="extractive_btn" autocomplete="off">
                  <label class="btn btn-outline-primary" for="extractive_btn">Extractive</label>

                  <input type="radio"  v-model="chosenSkillType" value="multiple-choice" class="btn-check" name="btnradio" id="btnradio2" autocomplete="off">
                  <label class="btn btn-outline-primary" for="btnradio2">Multiple Choice</label>

                  <input type="radio"  v-model="chosenSkillType" value="categorical" class="btn-check" name="btnradio" id="btnradio3" autocomplete="off">
                  <label class="btn btn-outline-primary" for="btnradio3">Categorical</label>

                  <input type="radio"  v-model="chosenSkillType" value="abstractive" class="btn-check" name="btnradio" id="btnradio4" autocomplete="off">
                  <label class="btn btn-outline-primary" for="btnradio4">Abstractive</label>

                  <input type="radio"  v-model="chosenSkillType" value="information-retrieval" class="btn-check" name="btnradio" id="btnradio5" autocomplete="off">
                  <label class="btn btn-outline-primary" for="btnradio5">IR</label>

                  <input type="radio"  v-model="chosenSkillType" value="" class="btn-check" name="btnradio" id="btnradio6" autocomplete="off">
                  <label class="btn btn-outline-primary" for="btnradio6">All</label>
                  
                </div>
                
              </div>
            </div>
          </div>
          
          <div class="container text-center" style="height: 20em; overflow-y: scroll;">
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3" >
              <div class="col mb-2" v-for="(skill, index) in filteredSkills" :key="skill.id">
                <div class="d-flex flex-wrap w-100 h-100">
                  <input class="btn-check" type="checkbox"
                    v-on:input="selectSkill(skill.id, index)"
                    v-bind:value="skill.id"
                    :disabled="waiting || (selectedSkills.length >= 3 && !selectedSkills.includes(skill.id))"
                    :id="skill.id"
                    >
                  <label class="btn btn-outline-primary d-flex align-middle align-items-center justify-content-center w-100 h-100" :for="skill.id" 
                          data-bs-toggle="tooltip" data-bs-placement="top" :title=skill.description style="--bs-bg-opacity: 1">
                            <span class="text-break">{{skill.name}}
                            <br>
                            <small class="text-muted">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
                                  <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                                  <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                                </svg>
                                {{skill.skill_type}}
                                <span class="px-1.5 text-gray-300">• </span>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-seam" viewBox="0 0 16 16">
                                  <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>
                                </svg>
                                {{skillModelType(skill)}}
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
</template>

<script>
import Vue from 'vue'

export default Vue.component('compare-skills', {
  props: ['selectorTarget', 'skillFilter'],
  data() {
    return {
      searchText: '',
      chosenSkillType: null,
      waiting: false,
      options: {
        selectedSkills: []
      }

    }
  },
  computed: {
    filteredSkills() {
        return this.searchText
          ? this.filteredSkills1.filter((item) => this.searchText
              .toLowerCase()
              .split(" ")
              .every(v => item.name.toLowerCase().includes(v)))
          : this.filteredSkills1
    },
    filteredSkills1() {
      // if number of None in selectedSkills is 3, then return all skills
      if (this.options.selectedSkills.filter(skill => skill == 'None').length === 3) {
        // if chosenSkillType is not empty, then filter by skill type
        if (this.chosenSkillType) {
          return this.availableSkills.filter(skill => skill.skill_type == this.chosenSkillType)
        } else {
          return this.availableSkills
        }
      } else {
        return this.availableSkillsBasedOnSettings
      }
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
    selectSkill(skill_id) {
      if(this.options.selectedSkills.includes(skill_id)){
        let index = this.options.selectedSkills.indexOf(skill_id)
        this.$set(this.options.selectedSkills, index, "None")
      }
      else{
        let index = this.options.selectedSkills.indexOf('None')
        this.$set(this.options.selectedSkills, index, skill_id)
      }
      this.$store.dispatch('selectSkill', { skillOptions: this.options, selectorTarget: this.selectorTarget })
      this.$emit('input', this.options, this.skillSettings)
      
    },
    skillModelType(skill){
      // if skill.default_skill_args is not null
      if (skill.default_skill_args) {
        return skill.default_skill_args['base_model']
      } else {
        return 'Others'
      }
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
  }
})
</script>
