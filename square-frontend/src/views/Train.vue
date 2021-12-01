<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <form v-on:submit.prevent="trainSkill">
    <Card>
      <template #leftItem>
        <router-link to="/skills" class="btn btn-outline-primary d-inline-flex align-items-center" role="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-left-square" viewBox="0 0 16 16">
            <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
            <path d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z"/>
          </svg>
          &nbsp;My skills
        </router-link>
      </template>
      <template #topItem>
        <h5 class="fw-light mb-0">{{ skill.name }}</h5>
        <span v-if="skill.is_published" class="badge bg-info ms-1 p-2">Published</span>
        <span v-else class="badge bg-secondary ms-1 p-2">Not Published</span>
      </template>
      <template #rightItem>
        <button class="btn btn-outline-primary d-inline-flex align-items-center" type="submit" :disabled="waitingTraining">
          <span v-if="waitingTraining" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-upload" viewBox="0 0 16 16">
            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
          </svg>
          &nbsp;{{ skill.is_published ? 'Overwrite' : 'Publish' }}
        </button>
      </template>
      <Alert v-if="success" class="alert-success" dismissible>{{ successMessage }}</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
      <Alert v-if="skill.is_published" class="alert-warning">This skill has already been published. Uploading new data will overwrite and retrain the model.</Alert>
      <div class="row mt-3">
        <div class="col">
          <label for="train_file" class="form-label">Training data</label>
          <input
              class="form-control form-control"
              id="train_file"
              type="file"
              v-on:change="handleFile($event)">
        </div>
      </div>
      <div class="row mt-3">
        <div class="col">
          <label for="dev_file" class="form-label">Dev data</label>
          <input
              class="form-control form-control"
              id="dev_file"
              type="file"
              v-on:change="handleFile($event)">
        </div>
      </div>
      <div class="row mt-3">
        <div class="col">
          Text files are expected to contain example questions seperated by line breaks. All file should be UTF-8 encoded and &lt; 5MB.
        </div>
      </div>
      <div v-if='skill.is_published || waitingUnpublishing' class="row mt-3">
        <div class="col">
          <Modal
              :waiting="waitingUnpublishing"
              :skill="skill.name"
              destructive-action="unpublish"
              v-on:callback="unpublishSkill"
              :callbackValue="skill.id" />
        </div>
      </div>
    </Card>
  </form>
</template>


<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'
import Card from '@/components/Card.vue'
import Modal from '@/components/Modal.vue'

export default Vue.component('train-skill', {
  data() {
    return {
      train_file: null,
      dev_file: null,
      success: false,
      successMessage: '',
      failure: false,
      failureMessage: '',
      waitingTraining: false,
      waitingUnpublishing: false
    }
  },
  components: {
    Alert,
    Card,
    Modal
  },
  computed: {
    skill() {
      return this.$store.state.mySkills.find(skill => skill.id === this.$route.params.id)
    }
  },
  methods: {
    trainSkill() {
      this.failure = false
      this.success = false
      this.waitingTraining = true
      this.$store.dispatch('SOCKET_train',  { id: this.skill.id, train_file: this.train_file, dev_file: this.dev_file })
    },
    unpublishSkill() {
      this.failure = false
      this.success = false
      this.waitingUnpublishing = true
      this.$store.dispatch('SOCKET_unpublish', { id: this.skill.id })
    },
    handleFile(event) {
      this.$data[event.target.id] = event.target.files[0]
    }
  },
  sockets: {
    train(val) {
      if (val.finished) {
        this.waitingTraining = false
        this.$store.dispatch('updateSkills')
            .then(() => this.$store.commit('initQueryOptions', { forceSkillInit: true }))
      } else if (val.error) {
        this.waitingTraining = false
        this.failure = true
        this.failureMessage = val.error
      } else if (val.msg) {
        this.success = true
        this.successMessage = val.msg
      }
    },
    unpublish(val) {
      if (val.finished) {
        this.waitingUnpublishing = false
        this.$store.dispatch('updateSkills')
            .then(() => this.$store.commit('initQueryOptions', { forceSkillInit: true }))
      } else if (val.error) {
        this.waitingTraining = false
        this.failure = true
        this.failureMessage = val.error
      } else if (val.msg) {
        this.success = true
        this.successMessage = val.msg
      }
    }
  }
})
</script>
