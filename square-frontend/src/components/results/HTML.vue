<!-- Component for a results with HTML. The results is sanitized before it is used. -->
<template>
  <div>
    <b-card-text v-html="sanitizedHTML"></b-card-text>
  </div>
</template>

<script>
import Vue from 'vue'
import { sanitize } from 'dompurify'

export default Vue.component('raw_html', {
  props: {
    result: Object
  },
  computed: {
    sanitizedHTML() {
      var html = this.result.result
      var sanitized = sanitize(html)
      return sanitized
    }
  }
})
</script>
