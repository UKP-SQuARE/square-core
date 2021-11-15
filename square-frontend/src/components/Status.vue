<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <span class="badge py-2" :class="this.bgColor">
    <span v-if="this.status === 'checking'" class="spinner-grow spinner-grow-sm" role="status" />
    {{ this.label }}
  </span>
</template>

<script>
import Vue from 'vue'
import { pingSkill } from '@/api'

export default Vue.component('status', {
  props: ['url'],
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
      this.testSkillUrl()
    }
  },
  methods: {
    testSkillUrl() {
      this.status = 'checking'
      pingSkill(this.url).then(() => {
        this.status = 'available'
      }).catch(() => {
        this.status = 'unavailable'
      })
    }
  },
  beforeMount() {
    this.testSkillUrl()
  }
})
</script>
