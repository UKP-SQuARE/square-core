<!-- The Skills Overview Page. The user can see their skills here. They can delete, edit and train (publish) existing skills or create a new skill. -->
<template>
  <Card title="My skills">
    <template #rightItem>
      <router-link to="/skills/new_skill" class="btn btn-outline-primary d-inline-flex align-items-center" role="button">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
        </svg>
        &nbsp;New
      </router-link>
    </template>
    <div class="list-group list-group-flush">
      <li
          v-for="skill in mySkills"
          :key="skill.id"
          class="list-group-item py-4">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{ skill.name }}</h5>
          <small>{{ skill.url }}</small>
        </div>
        <p class="mb-3">{{ skill.description }}</p>
        <Status :url="skill.url" />
        <span v-if="skill.is_published" class="badge bg-info ms-1 p-2">Published</span>
        <span v-else class="badge bg-secondary ms-1 p-2">Not Published</span>
        <div class="d-grid gap-2 d-flex mt-2">
          <router-link :to="{ name: 'skill', params: {id: skill.id}} " class="btn btn-outline-primary" role="button">Edit</router-link>
          <router-link :to="{ name: 'train', params: {id: skill.id}} " class="btn btn-outline-primary" role="button">Manage Publication</router-link>
          <Modal
              :skill="skill.name"
              destructive-action="delete"
              v-on:callback="deleteSkill"
              :callbackValue="skill.id"
              class="ms-auto" />
        </div>
      </li>
    </div>
    <div v-if="!mySkills.length" class="d-grid gap-2">
      <router-link to="/skills/new_skill" class="btn btn-primary d-inline-flex justify-content-center align-items-center" role="button">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square-fill" viewBox="0 0 16 16">
          <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3a.5.5 0 0 1 1 0z"/>
        </svg>
        &nbsp;New
      </router-link>
    </div>
  </Card>
</template>


<script>
import Vue from 'vue'
import Card from '@/components/Card.vue'
import Modal from '@/components/Modal.vue'
import Status from '@/components/Status.vue'

export default Vue.component('list-skills', {
  components: {
    Card,
    Modal,
    Status
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
  }
})
</script>
