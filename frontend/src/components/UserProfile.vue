<template>
    <div class="text-center">
      <b-img :src="profilePictureUrl" alt="Profile Picture" class="profile-picture" rounded="circle" />
      <h2>{{ user.name }}</h2>
      <!-- Additional user information can go here -->
    </div>
  </template>
  
  <script>
  export default {
    name: 'UserProfile',
    props: {
      user: {
        type: Object,
        required: true
      }
    },
    computed: {
        profilePictureUrl() {
        return this.user.profilePicture || 'https://upload.wikimedia.org/wikipedia/commons/b/b5/Windows_10_Default_Profile_Picture.svg';
        }
    }
  };
  </script>
  
  <style scoped>
    .profile-picture {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
    }
  </style>
  