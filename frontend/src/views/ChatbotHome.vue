<!-- The Home Page to choose an LLM to communicate with -->
<template>
  <div class="bg-light border rounded shadow p-3">

    <!-- Modal for Purchasing Model -->
    <div v-if="isModalVisible" class="modal fade show" style="display: block;" @click.self="toggleModal(false)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Purchase Model Access</h5>
            <button type="button" class="btn-close" aria-label="Close" @click="toggleModal(false)"></button>
          </div>
          <div class="modal-body">
            <p>Do you want to buy access to {{ selectedModelName }} for {{ selectedModelPrice }} points?</p>
            <div v-if="feedbackMessage"
                 :class="['feedback-message', feedbackMessageType === 'error' ? 'text-danger' : 'text-success']">
              {{ feedbackMessage }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-success btn-lg text-white" @click="unlockModel(selectedModelId)">Yes
            </button>
            <button type="button" class="btn btn-secondary btn-lg text-white" @click="toggleModal(false)">Cancel
            </button>
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
                          @click="toggleModal(true, model.id, model.name, model.price)"
                      >
                        Unlock
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                             class="bi bi-lock" viewBox="0 0 16 16">
                          <path
                              d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM5 8h6a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
                        </svg>
                      </button>
                      <span v-else class="mt-0">
                        <router-link :to="{ name: 'chatbot', modelName: selectedModelName }"
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
import {getProfile, putProfile, getLLMs, getLLMsByemail, getBadgeByTitle} from '@/api';

Vue.use(VueTippy);

export default Vue.component('chatbot-hub', {
  data() {
    return {
      searchText: '',
      currentPage: 1,
      pageCount: 0,
      waiting: false,
      allModels: [],
      availableModelNamesForEachLoggedUser: ['Phi'],
      availableModels: [],
      points: 0,
      overallPoints: 0,
      isModalVisible: false,
      selectedModelId: null,
      selectedModelName: '',
      selectedModelPrice: 0,
      feedbackMessage: '',
      feedbackMessageType: '',
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
  },
  watch: {
    '$store.state.userInfo': {
      handler(userInfo) {
        if (userInfo && Object.keys(userInfo).length > 0) {
          this.fetchProfile();
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
      const email = this.$store.state.userInfo.email;
      const headers = {};
      getProfile(headers, email).then(response => {
        this.points = response.data.currentPoints;
        this.overallPoints = response.data.overallPoints;
      }).catch(error => {
        console.error("Failed to fetch profile:", error);
      });
    },
    updateProfile() {
      const email = this.$store.state.userInfo.email;
      const headers = {};

      getProfile(headers, email).then(response => {
        const profileData = {
          ...response.data,
          currentPoints: this.points
        };

        putProfile(headers, email, profileData).then(response => {
          console.log(response.data)
        }).catch(error => {
          console.error("Failed to update profile:", error);
        });
      }).catch(error => {
        console.error("Failed to fetch profile for update:", error);
      });
    },
    toggleModal(visibility, modelId = null, modelName = '', modelPrice = 0) {
      this.isModalVisible = visibility;
      this.selectedModelId = modelId;
      this.selectedModelName = modelName;
      this.selectedModelPrice = modelPrice;
      if (!visibility) {
        this.feedbackMessage = '';
      }
    },
    async unlockModel(modelId) {
      if (!this.isUserLoggedIn()) {
        this.feedbackMessage = 'Log in to earn points and unlock models!';
        this.feedbackMessageType = 'error';
        return;
      }

      const selectedModel = this.availableModels.find(model => model.id === modelId);
      if (selectedModel) {
        this.selectedModelName = selectedModel.name;
        this.selectedModelPrice = selectedModel.price;
      } else {
        this.feedbackMessage = 'Model not found.';
        this.feedbackMessageType = 'error';
        return;
      }

      if (this.points < selectedModel.price) {
        this.feedbackMessage = `You do not have enough points. This model costs ${selectedModel.price} points.`;
        this.feedbackMessageType = 'error';
        return;
      }

      this.points -= selectedModel.price;

      try {
        const email = this.$store.state.userInfo.email;
        const headers = {};
        const profileResponse = await getProfile(headers, email);
        const profileData = profileResponse.data;
        profileData.currentPoints = this.points;

        if (!profileData.availableModels.includes(modelId)) {
          profileData.availableModels.push(modelId);
        }

// Construct the update payload
        const updatePayload = {
          email: profileData.email,
          overallPoints: profileData.overallPoints,
          currentPoints: profileData.currentPoints,
          Certificates: profileData.Certificates,
          Badges: profileData.Badges,
          Reviews: profileData.Reviews,
          availableModels: profileData.availableModels
        };

        const availableModelsCount = this.availableModels.filter(model => model.available === true).length;
        const badgeTitle = 'NLP Master';
        const badgeResponse = await getBadgeByTitle({}, badgeTitle);
        if (availableModelsCount >= 2 && !updatePayload.Badges.includes(badgeResponse.data.id)) {
          try {
            if (badgeResponse && badgeResponse.data) {
              updatePayload.Badges.push(badgeResponse.data.id);
              const updateResponse = await putProfile(headers, email, updatePayload);
              if (updateResponse && updateResponse.data) {
                this.feedbackMessage = 'Wow, you earned a Badge by unlocking the Model, check your profile!\n';
              } else {
                console.error("Failed to update profile with new badge:", badgeTitle);
              }
            } else {
              console.error("Badge already exists or failed to fetch badge by title:", badgeTitle);
            }
          } catch (error) {
            console.error("Error in badge assignment process:", error);
          }
        } else {
          this.feedbackMessage = 'Model unlocked successfully!';
          this.feedbackMessageType = 'success';
// Update profile even if no badge is awarded
          const updateResponse = await putProfile(headers, email, updatePayload);
          if (!updateResponse || !updateResponse.data) {
            console.error("Failed to update profile:", updatePayload);
          }
        }

        await this.fetchUserLLMs();
        await this.fetchAllLLMs();
      } catch (error) {
        console.error("Failed during model unlock process:", error);
        this.feedbackMessage = 'Failed to unlock the model. Please try again.';
        this.feedbackMessageType = 'error';
      } finally {
        setTimeout(() => {
          this.toggleModal(false);
          this.feedbackMessage = '';
        }, 2500);
      }
    },
    pageModelChange(pInfo) {
      this.currentPage = pInfo.pageNumber;
      this.updatePaginatedModels();
    },
    fetchAllLLMs() {
      const headers = {};
      getLLMs(headers).then(response => {
        this.allModels = response.data.map(llm => ({
          ...llm,
          available: this.availableModelNamesForEachLoggedUser.includes(llm.Name)
        }));
        this.setAvailableModels();
      }).catch(error => {
        console.error("Failed to fetch all LLMs:", error);
      });
    },
    fetchUserLLMs() {
      if (!this.isUserLoggedIn()) {
        return;
      }
      const email = this.$store.state.userInfo.email;
      const headers = {};
      getLLMsByemail(headers, email).then(response => {
        const userLLMs = response.data;
        const userLLMNames = userLLMs.map(llm => llm.Name);
        this.availableModelNamesForEachLoggedUser = [...new Set([...this.availableModelNamesForEachLoggedUser, ...userLLMNames])];
        this.setAvailableModels();
      }).catch(error => {
        console.error("Failed to fetch user LLMs:", error);
      });
    },
    setAvailableModels() {
      this.availableModels = this.allModels
          .map(llm => ({
            id: llm.id,
            name: llm.Name,
            description: llm.description || 'No description available',
            price: llm.price,
            available: this.availableModelNamesForEachLoggedUser.includes(llm.Name)
          }))
          .sort((a, b) => a.price - b.price);
    },

    updatePaginatedModels() {
      const start = (this.currentPage - 1) * 4;
      const end = start + 4;
      this.paginatedModels = this.filteredModels.slice(start, end);
    },

    isModelAvailable(model) {
      if (this.isUserLoggedIn()) {
        return model.name === 'Phi' ||
            this.availableModelNamesForEachLoggedUser.includes(model.name);
      } else {
        return model.name === 'Phi';
      }
    },
    isUserLoggedIn() {
      return this.$store.state.userInfo && Object.keys(this.$store.state.userInfo).length > 0;
    },
  },
  mounted() {
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
