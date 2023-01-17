<template id="expand-button">
  <div class="b-button" v-on:click="onClickButton">
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" v-bind:class="myButtonClass" :key="myButtonClass" viewBox="0 0 16 16">
      <path fill-rule="evenodd" d="M1.553 6.776a.5.5 0 0 1 .67-.223L8 9.44l5.776-2.888a.5.5 0 1 1 .448.894l-6 3a.5.5 0 0 1-.448 0l-6-3a.5.5 0 0 1-.223-.67z"/>
    </svg>
  </div>
</template>
<script>
import Vue from 'vue'

export default Vue.component('expand-buton', {
  template: '#expand-button',
  props: ['evaluation'],
  methods: {
    onClickButton() {
      this.isActive = !this.isActive
      this.myButtonClass = this.isActive ? "bi bi-chevron-compact-up" : "bi bi-chevron-compact-down"
      this.$root.$emit(this.evaluation.skill_id, this.isActive)
    }
  },
  data() {
    return {
      isActive: false,
      myButtonClass : "bi bi-chevron-compact-down"
    }
  }
})
</script>