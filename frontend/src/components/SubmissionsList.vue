<template>
  <div class="submissions-list">
    <div class="submission-entry" v-for="(submission, index) in topSubmissions" :key="index">
      <div class="llm-name-date">
        <div class="llm-name">{{ submission.LLM.Name }}</div>
        <div class="date-text">Updated {{ formatDate(submission.Date) }}</div>
      </div>
      <div class="details-points">
      <button class="details-btn" @click="viewReviewMessages(submission)">
        <div class="button-segment details">Details</div>
        <div class="button-segment points" :class="{ active: isActivePoints(submission) }">
          {{ submission.AchievedPoints }}
        </div>
      </button>
    </div>        
    </div>
    <div v-if="activeModal" class="modal fade show" style="display: block;" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="customModalLabel">Submission Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" style="max-height: 400px; overflow-y: auto;"> 
            <div v-for="(message, index) in activeModal.Messages" :key="index">
              <p><strong>{{ message.Prompt }}</strong></p>
              <p>{{ message.Response }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeModal" class="modal-backdrop fade show"></div> 
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
        // { key: 'Rating', label: 'Rating' },
        { key: 'AchievedPoints', label: 'Achieved Points' },
        { key: 'Date', label: 'Date' },
        { key: 'LLM', label: 'LLM Name' },
        { key: 'actions', label: 'Actions' }, // For the "View Details" button
      ];
    },
    topSubmissions() {
      return this.processSubmissions(this.submissions.slice(0, 5));
    }
  },
  data() {
    return {
      activeModal: null,
    };
  },
  methods: {
    processSubmissions(submissions) {
      return submissions.map(submission => {
        return {
          ...submission,
          LLM_Name: submission.LLM ? submission.LLM.Name : 'N/A' // Extract LLM Name
        };
      });
    },
    isActivePoints(submission) {
      // This method should return true if the points are the active segment
      // Replace this with your actual logic for determining the active segment
      submission = true;
      return submission; // Placeholder logic
    },
    viewReviewMessages(item) {
      this.activeModal = item;
    },
    closeModal() {
      this.activeModal = null;
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  }
};
</script>

<style scoped>
.submissions-list {
  font-family: 'Arial', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.submission-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
  width: 100%;
}

.details-points {
  justify-content: flex-end;
}


.llm-name-date {
  flex-grow: 1;
}

.llm-name {
  font-size: 1.2em;
  font-weight: bold;
}

.date-text {
  font-size: 0.8em;
  color: #6c757d;
}

.action-points {
  display: flex;
  align-items: center;
}

.details-btn {
  padding: 5px 15px;
  margin-right: 8px; /* space between button and points */
  border: 1px solid #dee2e6;
  background-color: #FFF;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  /* Ensure text alignment */
  text-align: center;
  /* Flex display to keep text centered */
  display: flex;
  align-items: center;
  justify-content: center;
}

.points {
  padding: 5px 10px;
  font-weight: bold;
  /* Style to indicate active status if needed */
}


.button-segment {
  padding: 5px 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-segment.details {
  border-right: 1px solid #dee2e6;
}

.button-segment.points {
  color: #007bff; /* Bootstrap primary color for example */
}

.button-segment.points.active {
  background-color: #ffffff;
  color: #000000;
}


.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 1.5em;
}

.modal-body {
  max-height: 400px;
  overflow-y: auto;
}

.details {
  padding: 5px 10px;
}

</style>
