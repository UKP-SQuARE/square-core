<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <select
      v-bind:value="value"
      v-on:input="$emit('input', $event.target.value)"
      class="form-select form-select-lg">
    <option>None</option>
    <option v-for="skill in skills" v-bind:value="skill.id" v-bind:key="skill.id">
      {{ skill.name }} — {{ skill.description }}
    </option>
  </select>
</template>

<script>
import Vue from 'vue'

export default Vue.component('skill-selector', {
  props: ['value', 'skills']
})
</script>
