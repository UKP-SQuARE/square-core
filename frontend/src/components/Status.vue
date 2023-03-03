<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <span class="badge d-inline-flex align-items-center py-2" :class="bgColor">
    <span v-if="status === 'checking'" class="spinner-grow spinner-grow-sm" role="status" />
    Skill: {{ label }}
  </span>
</template>

<script>
import Vue from 'vue'
import { skillHeartbeat } from '@/api'

export default Vue.component('skill-status', {
  props: ['id'],
  data() {
    return {
      /**
       * Values: 'checking', 'available', 'unavailable'
       */
      status: 'checking'
    }
  },
  computed: {
    bgColor() {
      let map = {'checking': 'bg-secondary', 'available': 'bg-success', 'unavailable': 'bg-danger'}
      return map[this.status]
    },
    label() {
      let map = {'checking': 'Checking ...', 'available': 'Available', 'unavailable': 'Unavailable'}
      return map[this.status]
    }
  },
  watch: {
    url: function () {
      this.checkSkillHealth()
    }
  },
  methods: {
    checkSkillHealth() {
      this.status = 'checking'
      skillHeartbeat(this.$store.getters.authenticationHeader(), this.id).then((response) => {
        this.status = response.data.is_alive ? 'available' : 'unavailable'
      }).catch(() => {
        this.status = 'unavailable'
      })
    }
  },
  beforeMount() {
    this.checkSkillHealth()
  }
})
</script>
