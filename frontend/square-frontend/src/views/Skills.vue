<template>
  <b-container>
    <h2 class="text-center">My skills</h2>
    <hr>
    <p v-if="username">You need to login to access your skills.</p>
    <b-card v-else v-for="skill in mySkills" v-bind:key="skill.id" v-bind:title="skill.name" class="offset-md-3 col-md-6">
      <b-button v-bind:to="{name: 'skill', params: {id: skill.id}}" variant="primary" class="mr-3">Edit</b-button>
      <b-button v-on:click="deleteSkill(skill.id)" variant="danger">Delete</b-button>
    </b-card>
    <b-button to="/skills/new_skill" variant="success" class="float-right">New Skill</b-button>
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
      return this.$store.state.username
    }
  },
  methods: {
    deleteSkill(skillId) {
      this.$store.dispatch("deleteSkill", {skillId: skillId})
    }
  },
  beforeMount(){
    this.$store.dispatch("updateMySkills")
  }
}
</script>
