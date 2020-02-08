<template>
  <b-container>
    <h2 class="text-center">My skills</h2>
    <hr>
    <b-button to="/skills/new_skill" variant="outline-success" class="float-right">New Skill</b-button>
    <b-card v-for="skill in mySkills" v-bind:key="skill.id" class="offset-md-3 col-md-6 mb-1">
      <b-card-title>
        {{skill.name}}
        <b-card-sub-title class="mt-1"> 
          <b-badge variant="info" v-if="skill.is_published">Published</b-badge> 
          <b-badge variant="secondary" v-else>Not Published</b-badge> 
        </b-card-sub-title>
      </b-card-title>
      <b-card-text>
        {{skill.scheme}}://{{skill.host}}/{{skill.base_path}}
      </b-card-text>
      <hr>
      <b-button v-bind:to="{name: 'skill', params: {id: skill.id}}" variant="outline-primary" class="float-left">Edit</b-button>
      <b-button v-on:click="deleteSkill(skill.id)" variant="outline-danger" class="float-right">Delete</b-button>
    </b-card>
  </b-container>
</template>


<script>
export default {
  name: 'skills',
  data() {
    return {
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
    this.$store.dispatch("updateSkills")
  }
}
</script>
