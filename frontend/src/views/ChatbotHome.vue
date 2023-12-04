<!-- The Home Page to choose an LLM to communicate with -->
<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <div class="col col-3 d-none d-md-block">
              <div class="container text-start"></div>
              <div class="row">
                <div class="col text-start">
                  <h4>Chatbot Rating Interface</h4>
                  <p class="mb-1">
                    <br>
                    Shape the future of conversational AI! <br><br>
                    Engage with various models <br> Provide valuable feedback <br> Earn points to unlock new features <br><br>
                    Start your journey today to become a certified LLM expert! <br><br>
                  </p>
                  <div v-if="isUserLoggedIn()" class="mt-5">
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
                  </div>
                  <div v-else>
                    <button class="btn btn-primary mt-3" @click="showLoginModal">
                      Log in to collect points
                    </button>
                  </div>
                </div>
              </div>
            </div>


            <div class="col col-md-9">
              <!-- Choose the LLM -->
              <span class="fw-bold">Available Models:</span>

              <!-- Search Bar -->
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

              <!-- Models -->
              <div class="row row-cols-2 g-3">
                <div class="col" v-for="model in paginatedModels" :key="model.id">
                  <div class="card h-100" :class="{'text-muted': !isModelAvailable(model)}"
                       style="height: 25vh !important;">
                    <div class="card-body d-flex flex-column align-items-center">
                      <h5 class="card-title text-primary">{{ model.name }}</h5>
                      <p class="text-muted text-center">
                        {{model.description}}
                      </p>
                      <span v-if="!isModelAvailable(model)" class="mt-auto">
                        <router-link :to="{ name: 'market', query: runQueryParams }"
                                     class="btn btn-primary btn-lg text-white">
                          Unlock
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                               class="bi bi-lock" viewBox="0 0 16 16">
                            <path
                                d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM5 8h6a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
                          </svg>
                        </router-link>
                      </span>
                      <span v-else class="mt-auto">
                        <router-link :to="{ name: 'chatbot', query: runQueryParams }"
                                     class="btn btn-danger btn-lg text-white">
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

          </div> <!-- end of skill list container -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import Vue from 'vue'
import VueTippy from "vue-tippy";
import {Page} from 'v-page'

Vue.use(VueTippy);

export default Vue.component('chatbot-hub', {
  data() {
    return {
      searchText: '',
      currentPage: 1,
      pageCount: 0,
      waiting: false,
      availableModels: [
        {id: 1, name: 'CommonsenseQA BERT Adapter', description: 'A model specialized in common sense question answering'},
        {id: 2, name: 'Llama', description: 'Versatile model adept at processing natural language'},
        {id: 3, name: 'ChatGPT-3.5', description: 'Advanced conversational agent for realistic dialogue'},
        {id: 4, name: 'ChatGPT-4.0', description: 'State-of-the-art language model with nuanced understanding'},
        {id: 5, name: 'Perplexity AI', description: 'AI designed for deep contextual comprehension and interaction.'},
      ],
      availableModelNamesForLoggedUser: ['CommonsenseQA BERT Adapter', 'ChatGPT-3.5'],
      points: 1500,
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
    filteredModels() {
      this.currentPage = 1;
      this.pageCount = Math.ceil(this.filteredModels.length / 4);
    },
  },
  methods: {
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
    updatePaginatedModels() {
      const start = (this.currentPage - 1) * 4;
      const end = start + 4;
      this.paginatedModels = this.filteredModels.slice(start, end);
    },
    isModelAvailable(model) {
      if (this.isUserLoggedIn()) {
        return this.availableModelNamesForLoggedUser.includes(model.name);
      } else {
        return this.availableModels[0].name === model.name;
      }
    },
    isUserLoggedIn() {
      return this.$store.state.userInfo && Object.keys(this.$store.state.userInfo).length > 0;
    },
  },
  mounted() {
    this.pageCount = Math.ceil(this.filteredModels.length / 4); // Initialize pageCount on mount
    this.updatePaginatedModels();
  }
})
</script>