<template>
  <b-container>
    <h2 class="text-center">My skills</h2>
    <hr>
    <b-button to="/skills/new_skill" variant="outline-success" class="float-right">New Skill</b-button>
    <b-card v-for="skill in mySkills" v-bind:key="skill.id" class="offset-md-3 col-md-6 mb-1">
      <b-card-title>
        {{skill.name}}
        <b-card-sub-title class="mt-1"> 
          <b-badge variant="info" v-if="skill.is_published" class="mr-1 mb-1">Published</b-badge> 
          <b-badge variant="secondary" v-else class="mr-1 mb-1">Not Published</b-badge> 

          <b-badge variant="secondary" v-if="skillStatuses[skill.name]==='checking'">Checking... <b-spinner type="grow" small></b-spinner></b-badge> 
          <b-badge variant="success" v-else-if="skillStatuses[skill.name]==='available'">Available</b-badge> 
          <b-badge variant="danger" v-else-if="skillStatuses[skill.name]==='unavailable'">Unavailable</b-badge>
          <br> {{skill.url}}
        </b-card-sub-title>
      </b-card-title>
      <b-card-text>
        {{skill.description}}
      </b-card-text>
      <hr>
      <b-button v-bind:to="{name: 'skill', params: {id: skill.id}}" variant="outline-primary" class="float-left">Edit</b-button>
      <b-button v-on:click="deleteSkill(skill.id)" variant="outline-danger" class="float-right">Delete</b-button>
    </b-card>
  </b-container>
</template>


<script>
import { pingSkill } from '@/api'
export default {
  name: 'skills',
  data() {
    return {
      skillStatuses: {}
    }
  },
  computed: {
    mySkills() {
      return this.$store.state.mySkills
    },
    user() {
      return this.$store.state.user
    }
  },
  methods: {
    deleteSkill(skillId) {
      this.$store.dispatch("deleteSkill", {skillId: skillId})
    }
  },
  beforeMount(){
    var self = this
    this.$store.dispatch("updateSkills")
    .then(() => {
      for(var i = 0; i<self.mySkills.length; i++) {
        var skill = self.mySkills[i]
        var skillName = skill.name
        self.$set(self.skillStatuses, skillName, "checking");
        (function(skillName) {
          pingSkill(skill.url)
          .then(() => {
            self.skillStatuses[skillName] = "available"
          })
          .catch(() => {
            self.skillStatuses[skillName] = "unavailable"
          })
        })(skillName);
      }
    })
  }
}
</script>
