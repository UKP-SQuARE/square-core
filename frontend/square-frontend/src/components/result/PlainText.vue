<!-- Component for simple plain text results. -->
<template>
  <b-card-text>{{result.text}}</b-card-text>
</template>

<script>
export default {
  name: "plain_text",
  props: {
    result: Object
  }
};
</script>
