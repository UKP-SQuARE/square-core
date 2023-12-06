<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="container-fluid">
      <div class="row">
        <!-- Profile Sidebar -->
        <div class="col-md-3">
          <div class="profile-sidebar">
            <!-- Profile Data -->
            <div class="tile-header">Profile</div>
            <user-profile :user="user" />
            
            <hr>
            <!-- Navigation Links -->
            <div class="profile-links">
              <router-link class="dropdown-item" to="/skills">My skills</router-link>
              <router-link class="dropdown-item" to="/evaluations">Evaluate skills</router-link>
              <a @click.prevent="$emit('account')" href="#" class="dropdown-item">Manage account</a>
            </div>
          </div>
        </div>

        <!-- Profile Main Content -->
        <div class="col-md-9">
          <div class="profile-main">
            <!-- Badges Section -->
            <div class="tile mb-3">
              <div class="tile-header">Badges</div>
              <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                <badges :badges="badges" />
              </div>
            </div>

            <!-- Certificates Section -->
            <div class="tile mb-3">
              <div class="tile-header">Certificates</div>
              <div class="certificates d-grid gap-1 d-md-flex justify-content-md-center">
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

            <!-- Leaderboard Section -->
            <div class="tile mb-3">
              <div class="tile-header">Leaderboard</div>
              <leaderboard-table :full.sync="isFullLeaderboard" />
            </div>

            <!-- Submissions Section -->
            <div class="tile mb-3">
              <div class="tile-header">Submissions</div>
              <submissions-list :submissions="submissions" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import Vue from "vue"
import { BootstrapVue } from "bootstrap-vue"
import "bootstrap-vue/dist/bootstrap-vue.css"
Vue.use(BootstrapVue)
import LeaderboardTable from '@/components/LeaderboardTable.vue'; 
import UserProfile from '@/components/UserProfile.vue';
import CertificateCard from '@/components/Certificates.vue';
import SubmissionsList from '@/components/SubmissionsList.vue';
import Badges from '@/components/Badges.vue';
export default {
  name: 'ProfilePage',
  components: {
    LeaderboardTable,
    UserProfile,
    CertificateCard,
    SubmissionsList,
    Badges
  },
  data() {
    return {
      isFullLeaderboard: false,
      // Mock user data, replace with real data from an API or store
      badges: [
        { id: 1, title: 'Expert', description: 'Top Contributor', icon: 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Earth_fluent_design_icon_2023_%28raster_graphics%29.png', type: '#ffd700' },
        { id: 2, title: 'Intermediate', description: 'Great Participation', icon: 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Earth_fluent_design_icon_2023_%28raster_graphics%29.png', type: 'silver' },
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



</style>
