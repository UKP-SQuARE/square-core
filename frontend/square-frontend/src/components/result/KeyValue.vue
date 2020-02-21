<!-- Component for results made out of key value pairs. -->
<template>
  <div>
    <b-card-text v-for="key_value in result.key_values" v-bind:key="key_value[0]">
      <strong>{{key_value[0]}}:</strong>
      {{key_value[1]}}
    </b-card-text>
  </div>
</template>

<script>
export default {
  name: "key_value",
  props: {
    result: Object
  }
};
</script>
