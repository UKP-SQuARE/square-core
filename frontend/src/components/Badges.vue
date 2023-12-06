<template>
  <div class="badges-container">
    <div v-for="badge in badges" :key="badge.id" class="badge-item">
      <!-- Badge Preview -->
      <div class="badge-preview" @click="showModal(badge.id)">
        <img :src="badge.icon" alt="Badge Icon" />
        <p>{{ badge.title }}</p>
      </div>

      <!-- Modal or Enlarged View -->
      <div v-if="activeModal === badge.id" class="modal fade show" style="display: block;" @click.self="closeModal">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <!-- Full Badge Details -->
            <div class="modal-header">
              <h5 class="modal-title">{{ badge.title }}</h5>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <img :src="badge.icon" alt="Badge Icon" class="full-badge-image" />
              <!-- Other badge details here -->
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeModal" class="modal-backdrop fade show"></div> <!-- Modal backdrop -->
  </div>
</template>

<script>
export default {
  name: 'ProfileBadges',
  props: {
    badges: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      activeModal: null,
    };
  },
  methods: {
    showModal(id) {
      this.activeModal = id;
    },
    closeModal() {
      this.activeModal = null;
    }
  }
};
</script>

<style scoped>
.badges-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4 columns by default */
  grid-gap: 10px; /* Adjust the gap as needed */
  /* Add more styling as needed */
}

@media (max-width: 768px) {
  .badges-container {
    grid-template-columns: repeat(3, 1fr); /* 3 columns on smaller screens */
  }
}

@media (max-width: 480px) {
  .badges-container {
    grid-template-columns: repeat(2, 1fr); /* 2 columns on very small screens */
  }
}

.badge-item {
  /* Styles for individual badge items */
}

.badge-preview {
  position: relative;
  width: 100px; /* Adjust as needed */
  height: 100px; /* Adjust as needed */
  display: flex;
  justify-content: center;
  align-items: center;
  /* background: url('path/to/your/image.jpg') no-repeat center center; */
  background-size: cover;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.badge-preview-text {
  position: absolute;
  text-align: center;
  width: 100%;
  color: white; /* Adjust text color as needed */
}
</style>

