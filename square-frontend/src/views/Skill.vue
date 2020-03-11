<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <b-container>
    <h2 class="text-center">{{originalName}}</h2>
    <hr />

    <b-alert v-model="success" variant="success" dismissible>Skill was updated successfully.</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>

    <b-button to="/skills" variant="outline-secondary" class="float-left">◁ Back to My Skills</b-button>

    <b-form class="offset-md-2 col-md-8" @submit="onSubmit">
      <b-form-group label="Name:" label-for="name">
        <b-form-input
          id="name"
          v-model="skill.name"
          type="text"
          required
          v-bind:placeholder="skill.name"
        ></b-form-input>
      </b-form-group>

      <b-form-group description="{scheme}://{host[:port]}/{base_path}">
        <label for="url" class="w-100">
          URL:
          <!-- Button and badges to display the availability status of the skill -->
          <!-- Button for testing
          <b-button
            @click="testSkillUrl"
            size="sm"
            variant="outline-primary"
            class="float-right"
          >Test URL</b-button>
          -->
          <b-badge
            variant="secondary"
            v-if="availableStatus==='checking'"
            class="float-right mr-2 mt-2"
          >
            Checking...
            <b-spinner type="grow" small></b-spinner>
          </b-badge>
          <b-badge
            variant="success"
            v-else-if="availableStatus==='available'"
            class="float-right mr-2 mt-2"
          >Available</b-badge>
          <b-badge
            variant="danger"
            v-else-if="availableStatus==='unavailable'"
            class="float-right mr-2 mt-2"
          >Unavailable</b-badge>
          <b-badge variant="secondary" v-else class="float-right mr-2 mt-2">Unknown</b-badge>
        </label>

        <b-form-input
          v-model="skill.url"
          required
          v-bind:placeholder="skill.url"
          v-on:change="testSkillUrl"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        label="Description:"
        label-for="description"
        description="Short description of the skill"
      >
        <b-form-input
          id="description"
          v-model="skill.description"
          type="text"
          v-bind:placeholder="skill.description"
        ></b-form-input>
      </b-form-group>

      <b-button v-if="isCreateSkill" type="submit" variant="outline-success" class="mr-2">Create</b-button>
      <b-button v-else type="submit" variant="outline-primary" class="mr-2">Save Changes</b-button>

      <b-button @click="resetSkill" variant="outline-danger" class="float-right">Reset Changes</b-button>
    </b-form>
  </b-container>
</template>


<script>
import { pingSkill } from "@/api";
export default {
  name: "skill",
  data() {
    return {
      skill: {
        name: "",
        url: "",
        description: ""
      },
      /**
       * The name for the title.
       * We do not use skill.name for this so that the title is only changed wenn the user updates the skill.
       */
      originalName: "",
      success: false,
      failure: false,
      failureMessage: "",
      /**
       * Values: "", "checking", "available", "unavailable"
       */
      availableStatus: ""
    };
  },
  computed: {
    /**
     * Decides if we want to create a new skill or edit an existing skill
     */
    isCreateSkill() {
      return this.$route.params.id === "new_skill";
    }
  },
  methods: {
    testSkillUrl() {
      this.availableStatus = "checking";
      pingSkill(this.skill.url)
        .then(() => {
          this.availableStatus = "available";
        })
        .catch(() => {
          this.availableStatus = "unavailable";
        });
    },
    onSubmit() {
      if (this.isCreateSkill) {
        this.createSkill();
      } else {
        this.updateSkill();
      }
    },
    updateSkill() {
      this.success = false;
      this.$store
        .dispatch("updateSkill", { skill: this.skill })
        .then(() => {
          this.originalName = this.skill.name;
          this.success = true;
          this.failure = false;
        })
        .then(() => {
          this.$store.commit("initQueryOptions", {forceSkillInit: true});
        })
        .catch(failureMessage => {
          this.failure = true;
          this.failureMessage = failureMessage;
        });
    },
    createSkill() {
      this.$store
        .dispatch("createSkill", { skill: this.skill })
        .then(() => this.$router.push("/skills"))
        .catch(error => {
          this.failure = true;
          this.failureMessage = error.data.msg;
        });
    },
    /**
     * Resets skill to the original values (empty values for new skill or the values in the state for existing skill)
     */
    resetSkill() {
      var oldURL = this.skill.url;
      if (this.isCreateSkill) {
        this.skill = {};
      } else {
        var skills = this.$store.state.mySkills;
        // Create a copy of the skill so we do not change the state
        this.skill = JSON.parse(
          JSON.stringify(skills.find(sk => sk.id === this.$route.params.id))
        );
      }
      // JS changes do not trigger change event, so we have to do it manually
      if (oldURL != this.skill.url) {
        this.testSkillUrl();
      }
    }
  },
  /**
   * Set original name and check availability of skill server for existing skill
   */
  beforeMount() {
    if (!this.isCreateSkill) {
      this.resetSkill();
      this.originalName = this.skill.name;
      this.testSkillUrl();
      console.log(this.skill)
    }
  }
};
</script>
