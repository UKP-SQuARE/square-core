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

                  <!-- CHANGE THE DESCRIPTION AND PURPOSE OF THIS PART -->

                  <h4>Domain
                    <svg
                        content="A Skill is a single domain if it was trained on a single dataset, and thus is expected to only perform well in that dataset.<br/>A Skill is a multi domain if it was trained on multiple datasets to be more general.<br/>A Skill is a Meta-Skill if it combines multiple Skills."
                        v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                        class="bi bi-info-circle" viewBox="0 0 16 16">
                      <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                      <path
                          d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
                    </svg>
                  </h4>

                  <span role="button" v-on:click="addRemoveScopeFilter('single_skill')"
                        class="btn btn-outline-primary btn-sm me-1 mb-1" id="single_skill">
                    Single Domain</span>
                  <span role="button" v-on:click="addRemoveScopeFilter('multi_skill')"
                        class="btn btn-outline-primary btn-sm me-1 mb-1" id="multi_skill">
                    Multi Domain</span>
                  <span role="button" v-on:click="addRemoveScopeFilter('meta_skill')"
                        class="btn btn-outline-primary btn-sm me-1 mb-1" id="meta_skill">
                    Meta-Skill</span>
                </div>
              </div>
            </div>
            <div class="col col-md-9">
              <!-- Write Selected Model in bold -->
              <span class="fw-bold">Selected Model:</span> {{ strSelectedModels }}

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

              <!-- Model cards -->
              <div class="col mb-2" v-for="(model) in paginatedModels" :key="model.id">
                <div class="card h-100" @click="navigateToModel(model)"
                     :class="{ 'disabled': !isModelAvailable(model) }">
                  <div class="card-body">
                    <h5 class="card-title">{{ model.name }}</h5>
                    <span v-if="!isModelAvailable(model)" class="locked-icon">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                               class="bi bi-lock" viewBox="0 0 16 16">
                            <path
                                d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM5 8h6a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
                          </svg>
                       </span>
                  </div>
                </div>
              </div>

              <!-- Pagination Component -->
              <v-page :total-row="filteredModels.length" align="center" v-model="currentPage" ref="page"
                      @page-change="pageModelChange" :page-size="4" language="en" :page-count="pageCount"></v-page>

            </div>
          </div>

        </div> <!-- end of skill list container -->
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
        {id: 1, name: 'CommonsenseQA BERT Adapter'},
        {id: 2, name: 'Llama'},
        {id: 3, name: 'ChatGPT-3.5'},
        {id: 4, name: 'ChatGPT-4.0'},
        {id: 5, name: 'Perplexity AI'}
      ],
      availableModelNamesForLoggedUser: ['CommonsenseQA BERT Adapter', 'ChatGPT-3.5'],
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
    filteredModels() {
      this.currentPage = 1;
      this.pageCount = Math.ceil(this.filteredModels.length / 4);
    },
  },
  methods: {
    navigateToModel(model) {
      this.$router.push({name: 'modelDetail', params: {modelId: model.id}});
    },
    pageModelChange(pInfo) {
      this.currentPage = pInfo.pageNumber;
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
})
</script>