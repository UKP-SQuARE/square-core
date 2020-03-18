<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <b-container>
    <h2 class="text-center">
      {{skill.name}}
      <b-badge variant="info" v-if="skill.is_published" class="ml-1 mb-1">Published</b-badge>
      <b-badge variant="secondary" v-else class="ml-1 mb-1">Not Published</b-badge>
    </h2>
    <hr />

    <b-alert v-model="success" variant="success" dismissible>{{successMessage}}</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>

    <b-button to="/skills" variant="outline-secondary" class="float-left">◁ Back to My Skills</b-button>

    <b-form class="offset-md-2 col-md-8" @submit.prevent="trainSkill">
      <b-form-group
        description="Text file containing example questions. Each line is treated as one example. File is expected to be UFT-8-encoded and smaller than 5MB."
      >
        <label
          for="file"
        >{{skill.is_published ? 'Upload training data (this will overwrite previous training data and retrain models):' : 'Upload training data:'}}</label>
        <b-form-file
          v-model="file"
          :state="Boolean(file)"
          name="file"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
          required
          no-drop
        ></b-form-file>
      </b-form-group>

      <b-button
        v-if="!waitingTraining"
        type="submit"
        variant="outline-primary"
        class="mr-2"
      >{{skill.is_published ? 'Retrain' : 'Train and Publish'}}</b-button>
      <b-button v-else type="submit" variant="outline-primary" class="mr-2" disabled>
        Training...
        <b-spinner small label="Spinning"></b-spinner>
      </b-button>

      <b-button
        v-if="skill.is_published && !waitingUnpublishing"
        v-b-modal="'modal-'+skill.name"
        variant="outline-danger"
        class="float-right"
      >Unpublish</b-button>
      <b-button
        v-else-if="skill.is_published && waitingUnpublishing"
        variant="outline-danger"
        class="float-right"
        disabled
      >
        Unpublishing...
        <b-spinner small label="Spinning"></b-spinner>
      </b-button>

      <b-modal v-bind:id="'modal-'+skill.name" title="Are you sure?">
        <p>Please confirm that you want to unpublish {{skill.name}}.</p>
        <p>You will have to retrain the skill if you want to publish it again.</p>
        <template v-slot:modal-footer>
          <b-button variant="outline-success" @click="$bvModal.hide('modal-'+skill.name)">Cancel</b-button>
          <b-button variant="outline-danger" @click="$bvModal.hide('modal-'+skill.name); unpublishSkill()">Unpublish</b-button>
        </template>
      </b-modal>
    </b-form>
  </b-container>
</template>


<script>
export default {
  name: "train",
  data() {
    return {
      file: null,
      success: false,
      successMessage: "",
      failure: false,
      failureMessage: "",
      waitingTraining: false,
      waitingUnpublishing: false
    };
  },
  computed: {
    skill() {
      var skills = this.$store.state.mySkills;
      return skills.find(sk => sk.id === this.$route.params.id);
    }
  },
  methods: {
    trainSkill() {
      this.failure = false;
      this.success = false;
      this.waitingTraining = true;
      this.$store.dispatch("SOCKET_train",  { id: this.skill.id, file: this.file });
    },
    unpublishSkill() {
      this.failure = false;
      this.success = false;
      this.waitingUnpublishing = true;
      this.$store.dispatch("SOCKET_unpublish", {id: this.skill.id});
    }
  },
  sockets: {
    train(val) {
      if (val.finished) {
        this.waitingTraining = false;
        this.$store.dispatch("updateSkills")
        .then(() => this.$store.commit("initQueryOptions", {forceSkillInit: true}));
      } else if (val.error) {
        this.waitingTraining = false;
        this.failure = true;
        this.failureMessage = val.error;
      } else if (val.msg) {
        this.success = true;
        this.successMessage = val.msg;
      }
    },
    unpublish(val) {
      if (val.finished) {
        this.waitingUnpublishing = false;
        this.$store.dispatch("updateSkills")
        .then(() => this.$store.commit("initQueryOptions", {forceSkillInit: true}));
      } else if (val.error) {
        this.waitingTraining = false;
        this.failure = true;
        this.failureMessage = val.error;
      } else if (val.msg) {
        this.success = true;
        this.successMessage = val.msg;
      }
    }
  }
};
</script>
