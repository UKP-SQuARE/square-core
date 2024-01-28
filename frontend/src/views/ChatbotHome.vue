<!-- The Home Page to choose an LLM to communicate with -->
<template>
  <div class="bg-light border rounded shadow p-3">

    <div v-if="isModalVisible" class="modal fade show" style="display: block;" @click.self="openPopup = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Purchase Model Access</h5>
            <button type="button" class="btn-close" aria-label="Close" @click="toggleModal(false)"></button>
          </div>
          <div class="modal-body">
            <p>Do you want to buy the model access for 1000 points?</p>
            <div v-if="feedbackMessage" :class="['feedback-message', feedbackMessageType === 'error' ? 'text-danger' : 'text-success']">
              {{ feedbackMessage }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-success btn-lg text-white" @click="unlockModel(selectedModelId)">Yes</button>
            <button type="button" class="btn btn-secondary btn-lg text-white" @click="toggleModal(false)">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <div class="col col-3 d-none d-md-block">
              <div class="container text-start"></div>
              <div class="row">

                <!-- Description and Points -->

                <!-- Description of the Chatbot Rating Interface
                <h4>Chatbot Rating Interface</h4>
                <p class="mb-1">
                  <br>
                  Shape the future of conversational AI! <br><br>
                  Engage with various! modelsProvide valuable feedback! Earn points to unlock new features!
                  Start your journey today to become a certified LLM expert!
                </p>
                -->
                <div v-if="isUserLoggedIn()">
                  <div class="col text-start">
                    <h4>Available Points:</h4>
                    <span class="badge bg-primary ms-auto" style="font-size: 1.5em;">
                      {{ points }}
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                           class="bi bi-award-fill" viewBox="0 0 16 16">
                      <path
                          d="m8 0 1.669.864 1.858.282.842 1.68 1.337 1.32L13.4 6l.306 1.854-1.337 1.32-.842 1.68-1.858.282L8 12l-1.669-.864-1.858-.282-.842-1.68-1.337-1.32L2.6 6l-.306-1.854 1.337-1.32.842-1.68L6.331.864z"/>
                      <path d="M4 11.794V16l4-1 4 1v-4.206l-2.018.306L8 13.126 6.018 12.1z"/>
                    </svg>
                    </span>
                    <div class="text-muted" style="font-size: 0.8em;">
                      Total Earned Points: {{ overallPoints }}
                    </div>
                    <!-- <h4>Leaderboard Place:</h4>
                    <span class="badge bg-primary ms-auto" style="font-size: 1.5em;">
                      {{ lbPlace }} out of 50
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                           class="bi bi-award-fill" viewBox="0 0 16 16">
                      <path
                          d="m8 0 1.669.864 1.858.282.842 1.68 1.337 1.32L13.4 6l.306 1.854-1.337 1.32-.842 1.68-1.858.282L8 12l-1.669-.864-1.858-.282-.842-1.68-1.337-1.32L2.6 6l-.306-1.854 1.337-1.32.842-1.68L6.331.864z"/>
                      <path d="M4 11.794V16l4-1 4 1v-4.206l-2.018.306L8 13.126 6.018 12.1z"/>
                    </svg>
                    </span> -->
                  </div>
                </div>
                <div v-else>
                  <router-link class="btn btn-primary mt-3" to="/signin">
                    Sign in to earn points!
                  </router-link>
                </div>
              </div>
            </div>


            <div class="col col-md-9">
              <!-- Choose the LLM -->
              <span class="fw-bold">Models:</span>

              <!-- Search Bar
              <div class="input-group input-group-sm mb-2">
                <span class="input-group-text" id="basic-addon1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                       class="bi bi-search"
                       viewBox="0 0 16 16">
                    <path
                        d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z">
                    </path>
                  </svg>
                </span>
                <input v-model="searchText" placeholder="Search Model" class="form-control form-control-xs"/>
              </div>
              -->

              <!-- Models -->
              <div class="row row-cols-2 g-3">
                <div class="col" v-for="model in paginatedModels" :key="model.id">
                  <div class="card h-100" :class="{'text-muted': !isModelAvailable(model)}"
                       style="height: 15vh !important;">
                    <div class="card-body d-flex flex-column align-items-center">
                      <h5 class="card-title text-primary">{{ model.name }}</h5>
                      <p class="text-muted text-center">
                        {{ model.description }}
                      </p>
                      <button
                          v-if="!isModelAvailable(model)"
                          class="btn btn-primary btn-sm text-white"
                          @click="toggleModal(true, model.id)"
                      >
                        Unlock
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                             class="bi bi-lock" viewBox="0 0 16 16">
                          <path
                              d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM5 8h6a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
                        </svg>
                      </button>
                      <span v-else class="mt-0">
                        <router-link :to="{ name: 'chatbot', query: runQueryParams }"
                                     class="btn btn-success btn-sm text-white">
                          Run
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                               class="bi bi-box-arrow-in-right" viewBox="0 0 16 16">
                            <path fill-rule="evenodd"
                                  d="M6 3.5a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 0-1 0v2A1.5 1.5 0 0 0 6.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-8A1.5 1.5 0 0 0 5 3.5v2a.5.5 0 0 0 1 0v-2z"/>
                            <path fill-rule="evenodd"
                                  d="M11.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H1.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                          </svg>
                        </router-link>
                      </span>
                    </div>
                  </div>
                </div>
              </div>


              <!-- Pagination Component -->
              <v-page :total-row="filteredModels.length" align="center" v-model="currentPage" ref="page"
                      @page-change="pageModelChange" :page-count="pageCount" :page-size-menu="[4]"
                      class="mt-4" hide-on-single-page="true" language="en"></v-page>
            </div>

            <!-- Promo -->
            <div class="bg-light border rounded shadow p-5 text-center">
              <div class="feature-icon bg-success bg-gradient">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                     class="bi bi-chat-heart" viewBox="0 0 16 16">
                  <path fill-rule="evenodd"
                        d="M2.965 12.695a1 1 0 0 0-.287-.801C1.618 10.83 1 9.468 1 8c0-3.192 3.004-6 7-6s7 2.808 7 6c0 3.193-3.004 6-7 6a8.06 8.06 0 0 1-2.088-.272 1 1 0 0 0-.711.074c-.387.196-1.24.57-2.634.893a10.97 10.97 0 0 0 .398-2m-.8 3.108.02-.004c1.83-.363 2.948-.842 3.468-1.105A9.06 9.06 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.437 10.437 0 0 1-.524 2.318l-.003.011a10.722 10.722 0 0 1-.244.637c-.079.186.074.394.273.362a21.673 21.673 0 0 0 .693-.125ZM8 5.993c1.664-1.711 5.825 1.283 0 5.132-5.825-3.85-1.664-6.843 0-5.132"/>
                </svg>
              </div>
              <h2 class="display-5">Chatbot Rating Interface</h2>
              <p class="lead fs-2">Engage with various <span class="text-success">ChatBots</span> and shape the future
                of conversational <span class="text-success">AI</span>!</p>
              <p class="lead fs-2">Provide valuable feedback. Earn <span class="text-success">points</span> to unlock
                new features.</p>
              <p class="lead fs-2"><span class="text-success">Start</span> your journey today to become a <span
                  class="text-success">certified</span> LLM expert!</p>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import Vue from 'vue'
import VueTippy from "vue-tippy";
import {Page} from 'v-page'
import { getProfile, putProfile, getLLMs, getLLMsByemail } from '@/api';

Vue.use(VueTippy);

export default Vue.component('chatbot-hub', {
  data() {
    return {
      searchText: '',
      currentPage: 1,
      pageCount: 0,
      waiting: false,
      allModels: [],
      availableModelNamesForEachLoggedUser: ['CommonsenseQA BERT Adapter', 'GPT-3.5-turbo'],
      availableModels: [],
      points: 0,
      overallPoints: 0,
      lbPlace: 2,
      isModalVisible: false,
      selectedModelId: null,
      feedbackMessage: '',
      feedbackMessageType: '', // 'success' or 'error'
    }
  },
  components: {
    'v-page': Page
  },
  computed: {
    filteredModels() {
      return this.availableModels.filter(model =>
          model.name.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    paginatedModels() {
      const start = (this.currentPage - 1) * 4;
      const end = start + 4;
      return this.filteredModels.slice(start, end);
    },
    modelPairs() {
      let pairs = [];
      for (let i = 0; i < this.paginatedModels.length; i += 2) {
        pairs.push(this.paginatedModels.slice(i, i + 2));
      }
      return pairs;
    },
  },
  watch: {
    '$store.state.userInfo': {
      handler(userInfo) {
        if (userInfo && Object.keys(userInfo).length > 0) {
          this.fetchProfile(); // Fetch profile when user info is updated (e.g., user logs in)
        }
      },
      deep: true
    },
    filteredModels() {
      this.currentPage = 1;
      this.pageCount = Math.ceil(this.filteredModels.length / 4);
    },
  },
  methods: {

    fetchProfile() {
      const email = this.$store.state.userInfo.email; // Get the email from the store
      const headers = {}; // Set headers if needed, for example for authentication
      getProfile(headers, email).then(response => {
        this.points = response.data.currentPoints; // Update current points
        this.overallPoints = response.data.overallPoints; // Update overall points
      }).catch(error => {
        console.error("Failed to fetch profile:", error);
        // Handle error, for example, show a notification
      });
    },
    toggleModal(visibility, modelId = null) {
      this.isModalVisible = visibility
      this.selectedModelId = modelId
    },

    updateProfile() {
      const email = this.$store.state.userInfo.email;
      const headers = {}; // Set headers if needed, for example for authentication

      // Fetch the latest profile data before attempting to update
      getProfile(headers, email).then(response => {
        const profileData = {
          ...response.data, // Spread operator to copy all properties
          currentPoints: this.points // Overwrite just the points
        };

        // Now send the updated profile data to the server
        putProfile(headers, email, profileData).then(response => {
          console.log(response.data)
        }).catch(error => {
          console.error("Failed to update profile:", error);
          // Handle error, for example, show a notification
        });
      }).catch(error => {
        console.error("Failed to fetch profile for update:", error);
        // Handle error, for example, show a notification
      });
    },
    async unlockModel(modelId) {
      if (!this.isUserLoggedIn()) {
        this.feedbackMessage = 'You need to log in to earn points and unlock new models.';
        this.feedbackMessageType = 'error';
        return;
      }

      if (this.points < 1000) {
        this.feedbackMessage = 'You do not have enough points.';
        this.feedbackMessageType = 'error';
        return;
      }

      // Deduct the cost of the model from the user's current points
      this.points -= 1000;

      try {
        const email = this.$store.state.userInfo.email;
        const headers = {}; // Set headers if needed, for example for authentication

        // Fetch the latest profile data
        const profileResponse = await getProfile(headers, email);
        const profileData = profileResponse.data;
        profileData.currentPoints = this.points;

        // Add the unlocked model to the user's available models if it's not already there
        if (!profileData.availableModels.includes(modelId)) {
          profileData.availableModels.push(modelId);
        }

        // Send the updated profile data to the server
        await putProfile(headers, email, profileData);

        // Fetch the updated list of user LLMs and all LLMs
        await this.fetchUserLLMs();
        await this.fetchAllLLMs();

        // Show success message
        this.feedbackMessage = 'Model unlocked successfully!';
        this.feedbackMessageType = 'success';
      } catch (error) {
        console.error("Failed during model unlock process:", error);
        this.feedbackMessage = 'Failed to unlock the model. Please try again.';
        this.feedbackMessageType = 'error';
      } finally {
        setTimeout(() => {
          this.toggleModal(false);
          this.feedbackMessage = '';
        }, 2000);
      }
    },
    pageModelChange(pInfo) {
      this.currentPage = pInfo.pageNumber;
      this.updatePaginatedModels();
    },
    handleLockClick() {
      if (!this.isUserLoggedIn()) {
        // Redirect to login page or show login modal
        this.showLoginModal();
      } else {
        // User is logged in but the model is not available
        // Handle accordingly, perhaps showing a message or an upgrade option
      }
    },
    fetchAllLLMs() {
      const headers = {}; // Set headers if needed, for example for authentication
      getLLMs(headers).then(response => {
        this.allModels = response.data; // Array of all LLMs
        this.setAvailableModels(); // Set available models based on all models and user-specific models
      }).catch(error => {
        console.error("Failed to fetch all LLMs:", error);
        // Handle error, for example, show a notification
      });
    },
    fetchUserLLMs() {
      if (!this.isUserLoggedIn()) {
        return;
      }
      const email = this.$store.state.userInfo.email;
      const headers = {}; // Set headers if needed, for example for authentication
      getLLMsByemail(headers, email).then(response => {
        const userLLMs = response.data; // Array of LLMs from the user's profile

        // Combine availableModelNamesForEachLoggedUser with names of fetched userLLMs, avoiding duplicates
        const userLLMNames = userLLMs.map(llm => llm.Name);
        this.availableModelNamesForEachLoggedUser = [...new Set([...this.availableModelNamesForEachLoggedUser, ...userLLMNames])];

        this.setAvailableModels(); // Set available models based on all models and user-specific models
      }).catch(error => {
        console.error("Failed to fetch user LLMs:", error);
        // Handle error, for example, show a notification
      });
    },
    setAvailableModels() {
      this.availableModels = this.allModels.map(llm => ({
        id: llm.id,
        name: llm.Name,
        description: this.getDescriptionForLLM(llm.Name),
        available: this.availableModelNamesForEachLoggedUser.includes(llm.Name)
      }));
    },
    getDescriptionForLLM(name) {
      const descriptions = {
        'CommonsenseQA BERT Adapter': 'A model specialized in common sense question answering',
        'Llama-2-7b-chat': 'Versatile model adept at processing natural language',
        'GPT-3.5-turbo': 'Advanced conversational agent for realistic dialogue',
        'ChatGPT-4.0': 'State-of-the-art model with nuanced understanding',
        'Perplexity AI': 'AI designed for deep contextual comprehension and interaction'
      };
      return descriptions[name] || 'No description available';
    },
    updatePaginatedModels() {
      const start = (this.currentPage - 1) * 4;
      const end = start + 4;
      this.paginatedModels = this.filteredModels.slice(start, end);
    },
    isModelAvailable(model) {
      if (this.isUserLoggedIn()) {
        return this.availableModelNamesForEachLoggedUser.includes(model.name);
      } else {
        return this.availableModels[0].name === model.name;
      }
    },
    isUserLoggedIn() {
      return this.$store.state.userInfo && Object.keys(this.$store.state.userInfo).length > 0;
    },
  },
  mounted() {
    // Fetch all LLMs and user-specific LLMs (if user is logged in)
    this.fetchAllLLMs();
    if (this.isUserLoggedIn()) {
      this.fetchProfile();
      this.fetchUserLLMs();
    }
    this.pageCount = Math.ceil(this.availableModels.length / 4);
    this.updatePaginatedModels();
  },
})
</script>
