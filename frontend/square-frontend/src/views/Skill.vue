<template>
  <b-container>
    <h2 class="text-center">{{originalName}}</h2>
    <hr>
    <b-alert v-model="success" variant="success" dismissible>
        Skill was updated successfully.
    </b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>
        There was a problem: {{failureMessage}}
    </b-alert>
    <b-button to="/skills" variant="outline-secondary" class="float-left">◁ Back to My Skills</b-button>
    <b-form class="offset-md-2 col-md-8" @submit="onSubmit">
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
      
      <b-button v-if="isCreateSkill" type="submit" variant="outline-success" class="mr-2">Create</b-button>
      <b-button v-else type="submit" variant="outline-primary" class="mr-2">Save Changes</b-button>
      <b-button @click="resetSkill" variant="outline-danger" class="float-right">Reset Changes</b-button>
    </b-form>
  </b-container>
</template>


<script>
export default {
  name: 'skill',
  data() {
    return {
      skill: {},
      originalName: "",
      success: false,
      failure: false,
      failureMessage: ""
    }
  },
  computed: {
    isCreateSkill() {
      return (this.$route.params.id === "new_skill") 
    }
  },
  methods: {
    onSubmit() {
      if (this.isCreateSkill){
        this.createSkill()
      } else {
        this.updateSkill()
      }
    },
    updateSkill() {
      this.success = false
      this.$store.dispatch("updateSkill", {skill: this.skill})
      .then(() => {
          this.originalName = this.skill.name
          this.success = true
          this.failure = false
          })
      .catch((failureMessage) => {
          this.failure = true
          this.failureMessage = failureMessage
        })
    },
    createSkill() {
      this.$store.dispatch("createSkill", {skill: this.skill})
      .then(() => this.$router.push("/skills"))
      .catch((error) => {
              this.failure = true
              this.failureMessage = error.data.msg
            })
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
      this.resetSkill()
      this.originalName = this.skill.name
    }
  }
}
</script>
