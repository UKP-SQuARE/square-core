<!-- The Skills Overview Page. The user can see their skills here. They can delete, edit and train (publish) existing skills or create a new skill. -->
<template>
  <div>
    <div class="card border-primary shadow mt-3">
      <h5 class="card-header fw-light text-center py-2">My skills</h5>
      <div class="card-body">
        <div class="list-group list-group-flush">
          <li
              v-for="skill in mySkills"
              :key="skill.id"
              class="list-group-item py-4">
            <div class="d-flex w-100 justify-content-between">
              <h5 class="mb-1">{{ skill.name }}</h5>
              <small>{{ skill.url }}</small>
            </div>
            <span v-if="skillStatuses[skill.name] === 'checking'" class="badge bg-secondary p-2">
              <span class="spinner-grow spinner-grow-sm" role="status" />
              Checking ...
            </span>
            <span v-if="skillStatuses[skill.name] === 'available'" class="badge bg-success p-2">
              Available
            </span>
            <span v-if="skillStatuses[skill.name] === 'unavailable'" class="badge bg-danger p-2">
              Unavailable
            </span>
            <span v-if="skill.is_published" class="badge bg-info ms-1 p-2">
              Published
            </span>
            <span v-else class="badge bg-secondary ms-1 p-2">
              Not Published
            </span>
            <p class="mb-1">{{ skill.description }}</p>
            <div class="d-grid gap-2 d-flex mt-3">
              <router-link :to="{ name: 'skill', params: {id: skill.id}} " class="btn btn-outline-primary" role="button">Edit</router-link>
              <router-link :to="{ name: 'train', params: {id: skill.id}} " class="btn btn-outline-primary" role="button">Manage Publication</router-link>
              <button class="btn btn-outline-danger ms-auto" data-bs-toggle="modal" :data-bs-target="`#deleteModal-${skill.id}`">Delete</button>
              <div class="modal fade" :id="`deleteModal-${skill.id}`" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                  <div class="modal-content">
                    <div class="modal-header">
                      <h5 class="modal-title" id="exampleModalLabel">Are you sure?</h5>
                      <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                      Please confirm that you want to delete <strong>{{ skill.name }}</strong>.
                    </div>
                    <div class="modal-footer">
                      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                      <button type="button" class="btn btn-danger" @click="deleteSkill(skill.id)">Delete</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </li>
        </div>
        <div class="d-grid gap-2">
          <router-link to="/skills/new_skill" class="btn btn-primary" role="button">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square-fill" viewBox="0 0 16 16">
              <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3a.5.5 0 0 1 1 0z"/>
            </svg>
            New
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import Vue from 'vue'
import { pingSkill } from '@/api'

export default Vue.component('skills', {
  data() {
    return {
      /**
       * Dictionary with skill names and their status.
       * Status is "checking", "available", "unavailable"
       */
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
      this.$store.dispatch('deleteSkill', { skillId: skillId })
    }
  },
  /**
   * Check availability status of all  skills
   */
  beforeMount() {
    let self = this
    this.$store.dispatch('updateSkills').then(() => {
      for (let i = 0; i < self.mySkills.length; i++) {
        let skill = self.mySkills[i]
        let skillName = skill.name
        self.$set(self.skillStatuses, skillName, 'checking');
        // Needed for correct variable values in the callback because loops
        (function(skillName) {
          pingSkill(skill.url)
              .then(() => {
                self.skillStatuses[skillName] = 'available'
              })
              .catch(() => {
                self.skillStatuses[skillName] = 'unavailable'
              })
        })(skillName)
      }
    })
  }
})
</script>
