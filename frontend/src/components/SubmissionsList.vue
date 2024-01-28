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
        { key: 'Date', label: 'Date', sortable: true },
        { key: 'LLM_Name', label: 'LLM Name' }
      ];
    },
    topSubmissions() {
      return this.processSubmissions(this.submissions.slice(0, 5));
    }
  },
  methods: {
    processSubmissions(submissions) {
      return submissions.map(submission => {
        return {
          ...submission,
          LLM_Name: submission.LLM ? submission.LLM.Name : 'N/A' // Extract LLM Name
        };
      });
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
  