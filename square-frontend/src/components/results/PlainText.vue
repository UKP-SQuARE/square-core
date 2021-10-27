<!-- Component for simple plain text results. -->
<template>
  <b-card-text>{{ result.result }}</b-card-text>
</template>

<script>
import Vue from 'vue'

export default Vue.component('plain_text', {
  props: {
    result: Object
  }
})
</script>
