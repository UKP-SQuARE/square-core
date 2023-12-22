<template>
  <div class="badges-container">
    <div v-for="badge in badges" :key="badge.id" class="badge-item"
      @mouseover="showModal(badge.id)" @mouseleave="closeModal">
      <!-- Badge Preview -->
      <div class="badge-preview" :style="{ backgroundColor: badge.type }">
        <img :src="badge.icon" alt="Badge Icon" />
        <p>{{ badge.title }}</p>
      </div>

       <!-- Bubble or Enlarged View -->
      <div v-if="activeModal == badge.id" class="badge-bubble">
        <div class="bubble-content">
          <h5 class="modal-title">{{ badge.title }}</h5>
          <!-- Other badge details here -->
        </div>
      </div>
    </div>
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

.modal {
  position: absolute;
  top: 120%; /* Adjust based on your layout */
  left: 50%;
  transform: translateX(-50%);
  z-index: 10; /* Ensure it's above other content */
  display: none; /* Hide by default */
}

.badge-item:hover .modal {
  display: block; /* Show the modal on hover */
}

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
  position: relative; /* This provides a positioning context for absolute children */
  z-index: 1;
}

.badge-preview {
  position: relative;
  width: 100px; /* Adjust as needed */
  height: 100px; /* Adjust as needed */
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  /* background: url('path/to/your/image.jpg') no-repeat center center; */
  background-size: cover;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  background-color: #ffd700; /* Adjust to match your badge color */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Example shadow */
  border: 2px solid #ffffff; /* Example border */
}

.badge-preview img {
  /* Adjust to properly size and position your badge icons */
  width: 60%; /* Example size */
  height: auto;
  padding: 10%; /* Example padding */
}

.badge-preview p {
  /* Style for badge title text */
  position: absolute;
  bottom: -20px; /* Adjust as needed */
  left: 50%;
  transform: translateX(-50%);
  margin: 0;
  font-size: 0.9rem; /* Example font size */
  color: #333; /* Example text color */
}

.badge-preview-text {
  position: absolute;
  text-align: center;
  width: 100%;
  color: white; /* Adjust text color as needed */
}

.badge-bubble {
  /* Position adjustments as necessary */
  position: absolute;
  bottom: -130%; /* You may need to adjust this */
  left: 50%;
  transform: translateX(-50%) translateY(-100%); /* Move up by the bubble's height */
  min-width: 200px; /* Adjust to your content */
  background: #FFFFFF;
  border-radius: 4px; /* Smaller border radius for a less rounded look */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px; /* Adjust padding to match your design */
  z-index: 100; /* Make sure it's above everything else */
  /* Other styles */
}

.modal-title {
  font-size: 1rem; /* Adjust font size as needed */
  font-weight: bold;
  margin-bottom: 8px;
}

/* Add additional styles for the content inside the bubble */
.bubble-content p {
  font-size: 0.9rem; /* Adjust font size as needed */
  color: #333; /* Adjust text color as needed */
  margin-bottom: 8px;
}

.badge-bubble::before {
  /* Adjust the notch to be at the top */
  content: '';
  position: absolute;
  top: -10px; /* Position the notch above the bubble */
  left: 50%;
  transform: translateX(-50%) rotate(45deg);
  width: 20px;
  height: 20px;
  background: #FFFFFF;
  border-radius: 2px;
  box-shadow: -2px -2px 2px rgba(0, 0, 0, 0.1);
}

.badge-item:hover .badge-bubble {
  display: block; /* Show the bubble on hover */
}
</style>

