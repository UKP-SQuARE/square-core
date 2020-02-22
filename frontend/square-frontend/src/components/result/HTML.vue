<!-- Component for a result with HTML. The result is sanitized before it is used. -->
<template>
  <div>
    <b-card-text v-html="sanitizedHTML"></b-card-text>
  </div>
</template>

<script>
import { sanitize } from "dompurify";
export default {
  name: "raw_html",
  props: {
    result: Object
  },
  computed: {
    sanitizedHTML() {
      var html = this.result.result;
      var sanitized = sanitize(html);
      console.log(sanitized);
      return sanitized;
    }
  }
};
</script>
