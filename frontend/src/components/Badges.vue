<template>
    <div class="badges-container">
      <div v-for="badge in badges" :key="badge.id" class="badge-item">
        <div :class="['badge', badge.type]">
          <span class="badge-icon">{{ badge.icon }}</span>
          <div class="badge-info">
            <h5 class="badge-title">{{ badge.title }}</h5>
            <p class="badge-description">{{ badge.description }}</p>
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
    }
  };
  </script>
  
  <style scoped>
  .badges-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
  }
  
  .badge-item {
    width: 200px;
  }
  
  .badge {
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    color: white;
  }
  
  .badge-icon {
    font-size: 2em;
  }
  
  .badge-info {
    margin-top: 10px;
  }
  
  .badge-title {
    margin: 0;
  }
  
  .gold {
    background-color: #ffd700;
  }
  
  .silver {
    background-color: #c0c0c0;
  }
  
  .bronze {
    background-color: #cd7f32;
  }
  
  /* Add more styles and badge types as needed */
  </style>
  