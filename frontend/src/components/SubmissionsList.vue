<template>
    <div class="submissions-list">
      <b-table striped hover :items="submissions" :fields="fields"></b-table>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SubmissionsList',
    props: {
      submissions: {
        type: Array,
        required: true
      }
    },
    computed: {
      fields() {
        return [
          { key: 'date', label: 'Date', sortable: true },
          { key: 'llmName', label: 'LLM Name' }
        ];
      }
    }
  };
  </script>
  
  <style scoped>
  /* Add any specific styles for your submissions list here */
  </style>
  