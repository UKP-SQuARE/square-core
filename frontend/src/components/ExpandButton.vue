<template id="expand-button">
  <div v-if="isActive" class="b-button" v-on:click="onClickButton">
    <BIconChevronCompactUp width="32" height="32"></BIconChevronCompactUp>
  </div>
  <div v-else class="b-button" v-on:click="onClickButton">
    <BIconChevronCompactDown width="32" height="32"></BIconChevronCompactDown>
  </div>
</template>
<script>
import Vue from 'vue'
import { BIconChevronCompactDown, BIconChevronCompactUp } from 'bootstrap-vue'

export default Vue.component('expand-buton', {
  template: '#expand-button',
  props: ['evaluation'],
  components: {
    BIconChevronCompactDown,
    BIconChevronCompactUp
  },
  methods: {
    onClickButton() {
      this.isActive = !this.isActive
      this.$root.$emit(this.evaluation.evaluation_id, this.isActive)
    }
  },
  data() {
    return {
      isActive: false
    }
  }
})
</script>