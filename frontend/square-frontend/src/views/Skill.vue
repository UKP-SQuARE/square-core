<template>
  <b-container>
    <h2 class="text-center">{{originalName}}</h2>
    <hr>
    <b-form @submit="updateSkill" class="offset-md-2 col-md-8">
      <b-form-group label="Name:" label-for="name" >
        <b-form-input id="name" v-model="skill.name" type="text" required v-bind:placeholder="skill.name" ></b-form-input>
      </b-form-group>

      <b-form-group label="URL to the skill:" label-for="url" description="scheme :// host[:port] / base_path">
        <b-input-group id="url">
          <b-form-input v-model="skill.scheme" required v-bind:placeholder="skill.scheme"></b-form-input>
          <b-input-group-prepend is-text>://</b-input-group-prepend>
          <b-form-input v-model="skill.host" required v-bind:placeholder="skill.host"></b-form-input>
          <b-input-group-prepend is-text>/</b-input-group-prepend>
          <b-form-input v-model="skill.base_path" required v-bind:placeholder="skill.base_path"></b-form-input>
        </b-input-group>
      </b-form-group>

      <b-form-group>
        <b-form-checkbox v-model="skill.is_published" switch>
            Publish this skill
        </b-form-checkbox>
      </b-form-group>
      

      <b-button type="submit" variant="primary" class="mr-2">Update Skill</b-button>
      <b-button @click="resetSkill" variant="danger">Reset</b-button>
    </b-form>
  </b-container>
</template>


<script>
export default {
  name: 'skill',
  data() {
    return {
      skill: {},
      originalName: ""
    }
  },
  methods: {
    updateSkill() {
      this.$store.dispatch("updateSkill", {skill: this.skill})
      
    },
    resetSkill() {
      if (this.$route.params.id === "new_skill") {
        this.skill = {
          name: "",
          is_published: false,
          scheme: "",
          host: "",
          base_path: ""
        }
      } else {
        var skills = this.$store.state.mySkills
        this.skill = JSON.parse(JSON.stringify(skills.find(sk => sk.id === this.$route.params.id)))
      }
    }
  },
  beforeMount(){
    if (this.$route.params.id === "new_skill") {
      this.originalName = "New Skill"
      this.skill = {
        name: "",
        is_published: false,
        scheme: "",
        host: "",
        base_path: ""
      }
    } else {
      this.originalName = this.skill.name
      this.resetSkill()
    }
  }
}
</script>
