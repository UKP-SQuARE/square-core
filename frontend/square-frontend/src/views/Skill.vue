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

      <b-form-group description="{scheme}://{host[:port]}/{base_path}">
          <label for="url" class="w-100">URL: 
            <b-button @click="testSkillUrl" size="sm" variant="outline-primary" class="float-right">Test URL</b-button>
            <b-badge variant="secondary" v-if="availableStatus==='checking'" class="float-right  mr-2 mt-2">Checking... <b-spinner type="grow" small></b-spinner></b-badge> 
            <b-badge variant="success" v-else-if="availableStatus==='available'" class="float-right  mr-2 mt-2">Available</b-badge> 
            <b-badge variant="danger" v-else-if="availableStatus==='unavailable'" class="float-right  mr-2 mt-2">Unavailable</b-badge> 
            <b-badge variant="secondary" v-else class="float-right mr-2 mt-2">Unknown</b-badge> 
          </label>
          <b-form-input v-model="skill.url" required v-bind:placeholder="skill.url"></b-form-input>
      </b-form-group>

      <b-form-group label="Description:" label-for="description" description="Short description of the skill">
        <b-form-input id="description" v-model="skill.description" type="text" v-bind:placeholder="skill.description" ></b-form-input>
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
import { pingSkill } from '@/api'
export default {
  name: 'skill',
  data() {
    return {
      skill: {},
      originalName: "",
      success: false,
      failure: false,
      failureMessage: "",
      availableStatus: ""
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
    testSkillUrl() {
      this.availableStatus = "checking"
      pingSkill(this.skill.url)
      .then(() => {
        this.availableStatus = "available"
      })
      .catch(() => {
        this.availableStatus = "unavailable"
      })
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
          url: "",
          description: ""
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
        url: "",
        description: ""
      }
    } else {
      this.resetSkill()
      this.originalName = this.skill.name
    }
  }
}
</script>
