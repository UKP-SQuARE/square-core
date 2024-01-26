<template>
    <div class="text-center">
      <b-img :src="profilePictureUrl" alt="Profile Picture" class="profile-picture" rounded="circle" />
      <div class="tile-header">{{ user.name }}</div>
      <div class="tile-header">{{ user.email }}</div>
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
    mounted() {
      console.log(this.user); // Check the user data
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
  