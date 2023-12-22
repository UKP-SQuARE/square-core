<!-- <template>
    <div class="submissions-list">
      <b-table striped hover :items="submissions" :fields="fields"></b-table>
    </div>
</template> -->
  
<template>
  <div class="submissions-list">
    <b-table striped hover :items="topSubmissions" :fields="fields"></b-table>
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
    },
    topSubmissions() {
      return this.submissions.slice(0, 5);
    }
  }
};
</script>
  
<style scoped>
.submissions-list {
  max-height: 400px; /* Adjust the height as needed */
  overflow-y: auto;
}
</style>
  