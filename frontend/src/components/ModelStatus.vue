<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
    <span class="badge d-inline-flex align-items-center py-2" :class="bgColor">
      <span v-if="status === 'checking'" class="spinner-grow spinner-grow-sm" role="status" />
      &nbsp;{{modelIdentifier}}: {{ label }}
    </span>
  </template>
  
  <script>
  import Vue from 'vue'
  import { modelHeartbeat } from '@/api'
  
  export default Vue.component('model-status', {
    props: ['modelIdentifier', 'modelKey'],
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
      modelIdentifier: function () {
        this.checkModelHealth()
      }
    },
    methods: {
        checkModelHealth() {
          this.status = 'checking'
          modelHeartbeat(this.$store.getters.authenticationHeader(), this.modelIdentifier).then((response) => {
            this.status = response.data[0].is_alive ? 'available' : 'unavailable'
          }).catch(() => {
            this.status = 'unavailable'
          })
      }
    },
    beforeMount() {
      this.checkModelHealth()
    }
  })
  </script>
  