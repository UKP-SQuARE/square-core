<template>
    <div class="profile-container">
      <div class="profile-container">
        <div class="profile-sidebar">
          <!-- Profile Data -->
          <div class="tile">
            <div class="tile-header">Profile</div>
            <user-profile :user="user" />

            <!-- Navigation Links -->
            <div class="profile-links">
              <!-- Link to My Skills Page -->
              <router-link class="dropdown-item" to="/skills">My skills</router-link>

              <!-- Link to Evaluate Skills Page -->
              <router-link class="dropdown-item" to="/evaluations">Evaluate skills</router-link>

              <!-- Manage Account -->
              <a @click.prevent="$emit('account')" href="#" class="dropdown-item">Manage account</a>
            </div>
          </div>
        </div>
      </div>
      <div class="profile-main">
        <!-- Badges, Certificates, Leaderboard, Submissions -->
        <div class="tile">
          <div class="tile-header">Badges</div>
          <badges :badges="badges" />
        </div>
        <div class="tile">
          <div class="tile-header">Certificates</div>
          <div class="certificates">
            <certificate-card
              v-for="certificate in certificates"
              :key="certificate.id"
              :certificate-id="certificate.id"
              :certificate-title="certificate.title"
              :student-name="certificate.studentName"
              :score="certificate.score"
              :evaluation-type="certificate.evaluationType"
              :issue-date="certificate.issueDate"
            />
          </div>
        </div>
        <div class="profile-leaderboard">
            <h3>Mini Leaderboard</h3>
            <show-leaderboard v-if="showFullLeaderboard"></show-leaderboard>
            <button @click="toggleLeaderboard">
            {{ showFullLeaderboard ? 'Hide' : 'Extend' }}
            </button>
        </div>
        <div class="tile">
        <div class="tile-header">Submissions</div>
            <submissions-list :submissions="submissions" />
        </div>
      </div>
    </div>
</template>

<script>
import ShowLeaderboard from '../views/Leaderboard.vue'; 
import UserProfile from '@/components/UserProfile.vue';
import CertificateCard from '@/components/Certificates.vue';
import SubmissionsList from '@/components/SubmissionsList.vue';
import Badges from '@/components/Badges.vue';
export default {
  name: 'ProfilePage',
  components: {
    ShowLeaderboard,
    UserProfile,
    CertificateCard,
    SubmissionsList,
    Badges
  },
  data() {
    return {
      showFullLeaderboard: false,
      // Mock user data, replace with real data from an API or store
      badges: [

        { id: 1, title: 'Expert', description: 'Top Contributor', icon: 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Eslogan_Oficial.png', type: 'gold' },
        { id: 2, title: 'Intermediate', description: 'Great Participation', icon: 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Eslogan_Oficial.png', type: 'silver' },
      ],
      submissions: [
        { date: '2023-11-12', llmName: 'Llama-2' },
        { date: '2023-11-23', llmName: 'phi-1_5' },
      ],
      certificates: [
        {
          id: 1,
          title: 'Certificate of Excellence',
          studentName: 'John Doe',
          score: '95%',
          evaluationType: 'Language Model Proficiency',
          issueDate: 'January 1, 2023'
        },
      ],
      user: {
        name: 'John Doe',
        bio: 'Lorem ipsum dolor sit amet...',
        // profilePicture: 'tbd',
        email: 'john@example.com',
        phone: '123-456-7890',
        posts: [
          { id: 1, title: 'Post 1' },
          { id: 2, title: 'Post 2' },
        ],
      },
      
    };
  },
  methods: {
        toggleLeaderboard() {
            this.showFullLeaderboard = !this.showFullLeaderboard;
        },
  },
};
</script>

<style scoped>
.profile-container {
  display: grid;
  grid-template-columns: 1fr 2fr; /* 1:2 ratio for sidebar:main */
  gap: 20px;
  width: 90%; /* Using 90% of the screen width */
  margin: auto; /* Centering the grid */
  padding: 20px;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tile {
  background: #fff; /* or any color you prefer */
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Tiles grow to fill the space */
}

.tile-header {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 15px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .profile-container {
    grid-template-columns: 1fr; /* Full width for smaller screens */
  }
}

.profile-sidebar {
  /* Styles for the sidebar */
}

.badges, .certificates, .leaderboard, .submissions {
  margin-bottom: 20px;
  /* Additional styling for each section */
}

.profile-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: auto;
  padding: 20px;
}

.profile-header {
  text-align: center;
}

.profile-picture {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
}

.info-section, .posts-section {
  margin-top: 20px;
}

</style>
