<template>
  <div>
    <div class="bg-light border rounded shadow p-3">
      <div class="w-100">
        <div class="mb-1">
          <div class="container-fluid">
            <div class="row">
              <div class="col col-4 d-none d-md-block">
                <div style="height: 35rem; overflow-y: auto; overflow-x: hidden;">
                  <form class="form-inline" @submit.prevent="saveKey">
                    <div class="form-group pb-2">
                      <div class="row">
                        <div class="col-9">
                          <label for="open-ai-key" class="form-label">OpenAI key (locally stored)</label>
                          <input type="password" class="form-control" id="open-ai-key" placeholder="OpenAI key"
                            title="Your key is stored locally and not shared with anyone" v-model="openAIApiKey" />
                        </div>
                        <div class="col-3 ps-0 d-flex align-items-end">
                          <button type="submit" class="btn btn-primary px-3">
                            Save
                          </button>
                        </div>
                      </div>
                    </div>
                    <hr />
                    <div class="form-group">
                      <label for="selectedModel" class="form-label">Model</label>
                      <select v-model="modelConfig.selectedModel" class="form-select" id="selectedModel">
                        <option v-for="model in modelList" :key="model.id" :value="model.id">
                          {{ model.id }}
                        </option>
                      </select>
                    </div>

                    <hr />

                    <div class="form-group">
                      <label for="selectedDataset" class="form-label">Dataset (to show examples form)</label>
                      <select v-model="selectedDatasetName" class="form-select" id="selectedDataset">
                        <option v-for="dataset in datasetNameList" :key="dataset" :value="dataset">
                          {{ dataset }}
                        </option>
                      </select>
                    </div>

                    <hr />
                    <div class="accordion" id="configControl">
                      <div class="accordion-item">
                        <h2 class="accordion-header" id="headingOne">
                          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            Model Controls
                          </button>
                        </h2>
                        <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne"
                          data-bs-parent="#configControl">
                          <div class="accordion-body">
                            <hr />
                            <div class="form-group">
                              <label for="tempRange" class="form-label">Tempreture: {{ this.modelConfig.temperature
                              }}</label>
                              <input v-model="modelConfig.temperature" type="range" class="form-range" min="0" max="1"
                                step="0.1" id="tempRange">
                            </div>
                            <hr />
                            <div class="form-group">
                              <label for="maxTokens" class="form-label">Max Tokens</label>
                              <input type="number" class="form-control" id="maxTokens" min="0" max="32768"
                                v-model="modelConfig.maxTokens" />
                            </div>
                            <hr />
                            <div class="form-group">
                              <label for="top_pRange" class="form-label">top_p: {{ this.modelConfig.top_p }}</label>
                              <input v-model="modelConfig.top_p" type="range" class="form-range" min="0" max="1"
                                step="0.1" id="top_pRange">
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
              <div class="col col-md-8 rounded">

                <form class="form" @submit.prevent="getSensitivity">

                  <div class="me-auto mt-4 mt-md-0">
                    <div class="bg-light border border-primary rounded h-100 p-3">
                      <div class="w-100">
                        <label for="originalInput" class="form-label">1. Enter your original input</label>
                        <textarea v-model="currentOriginalInput" @keydown.enter.exact.prevent
                          class="form-control form-control mb-2" style="resize: none; height: calc(48px);"
                          id="originalInput" placeholder="original input" required />
                        <p v-if="currentExamples.length > 0" class="form-label">Or try one of these examples</p>
                        <span role="button" v-for="(example, index) in currentExamples" :key="index"
                          v-on:click="selectExample(example)" class="badge bg-success m-1 text-wrap lh-base">{{
                            example.original
                          }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="me-auto mt-4 pt-4 mt-md-0">
                    <div class="bg-light border border-secondary rounded h-100 p-3">
                      <div class="w-100">
                        <div class="row">
                          <label for="perturbed_loop" class="form-label">2. Enter your perturbed input</label>
                          <div class="row g-0" v-for="(choice, index) in listPerturbedInput" :key="index"
                            id="perturbed_loop">
                            <div class="col-sm">
                              <div class="input-group input-group-sm mb-3 px-3">
                                <span class="input-group-text" id="basic-addon1">{{ index + 1 }}</span>
                                <input v-model="listPerturbedInput[index]" type="text"
                                  class="form-control form-control-sm" required>
                              </div>
                            </div>
                          </div>
                          <div class="form-inline">
                            <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addChoice">Add
                              Input</button>
                            <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeChoice">Remove
                              Input</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="pt-4  d-flex justify-content-center w-100">
                    <button type="submit" class="btn btn-danger btn-lg shadow text-white d-flex align-items-center"
                      :disabled="waiting">
                      <span v-show="waiting" class="spinner-border spinner-border-sm" role="status" />
                      &nbsp;Calculate Sensitivity&nbsp;&nbsp;
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                        class="bi bi-box-arrow-right" viewBox="0 0 16 16">
                        <path fill-rule="evenodd"
                          d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z" />
                        <path fill-rule="evenodd"
                          d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z" />
                      </svg>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="position-fixed bottom-0 d-flex justify-content-center w-100 p-3">
        <div id="toastBootstrap" class="toast text-white bg-primary border-0" role="alert" aria-live="assertive"
          aria-atomic="true" v-bind:class="{ show: showSuccessToast }">
          <div class="d-flex">
            <div class="toast-body">
              Key was saved successfully.
            </div>
          </div>
        </div>
      </div>
      <!-- <div class="position-fixed bottom-0 d-flex justify-content-center w-100 p-3">
        <div id="toastBootstrapError" class="toast text-white bg-danger border-0" 
        role="alert" aria-live="assertive" aria-atomic="true" v-bind:class="{ show: errorToast.show }">
          <div class="d-flex">
            <div class="toast-body">
              {{ errorToast.message }}
            </div>
          </div>
        </div>
      </div> -->
    </div>

    <div v-if="showResults" class="bg-light border rounded shadow p-3 mt-4">
      <div class="w-100">
        <div class="mb-1">
          <div class="container-fluid">
            <h1>
              Model {{ modelConfig.selectedModel }} has a sensitivity of {{ currentModelSensitivity }}.
            </h1>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { OpenAI } from "langchain/llms/openai";
import { PromptTemplate } from "langchain/prompts";

export default {
  name: "sensitivity-view",
  data: () => ({
    generativeModel: null,
    openAIApiKey: "",
    modelList: [],
    modelConfig: {
      selectedModel: "gpt-3.5-turbo-instruct",
      temperature: 0.8,
      maxTokens: 64,
      top_p: 1,
    },
    currentModelSensitivity: 0,
    showSuccessToast: false,
    currentOriginalInput: "",
    currentExamples: [],
    listPerturbedInput: ["", "", "", "", ""],
    waiting: false,
    selectedDatasetName: "cola",
    datasetNameList: [],
    datasets: {},
    exampleNumber: 3,
    showResults: false,
    // errorToast: {
    //   show: false,
    //   message: ""
    // },
  }),

  created() {
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    if (this.openAIApiKey != null) {
      this.initModel();
      this.fetchModels();
    }
    this.getDatasets();
    this.getExamples();
  },

  methods: {
    saveKey() {
      localStorage.setItem("openAIApiKey", this.openAIApiKey);
      this.showSuccessToast = true;
    },

    selectExample(example) {
      this.currentOriginalInput = example.original;
      for (let i = 0; i < this.listPerturbedInput.length; i++) {
        this.listPerturbedInput[i] = Object.entries(example.synthetic)[i][1]
      }
    },

    async initModel() {
      // see https://js.langchain.com/docs/modules/model_io/models/llms/integrations/openai
      this.generativeModel = new OpenAI({
        model: this.modelConfig.selectedModel,
        openAIApiKey: this.openAIApiKey,
        temperature: this.modelConfig.temperature,
        maxTokens: this.modelConfig.maxTokens,
        top_p: this.modelConfig.top_p,
      });
    },

    addChoice() {
      this.listPerturbedInput.push("");
    },

    removeChoice() {
      this.listPerturbedInput.pop();
    },

    async getSensitivity() {
      this.waiting = true;
      if (this.selectedDatasetName === 'cola') {
        const results = [];
        let prompt = await this.getPrompt(this.currentOriginalInput);
        let res = await this.generativeModel.call(prompt);
        results.push(res.trim());

        for (let i = 0; i < this.listPerturbedInput.length; i++) {
          prompt = await this.getPrompt(this.listPerturbedInput[i]);
          res = await this.generativeModel.call(prompt);
          results.push(res.trim());
        }
        console.log(results);
        this.currentModelSensitivity = this.calculateSensitivity(results);
        this.showResults = true;
      }
      this.waiting = false;
    },

    calculateSensitivity(results) {
      let s = 1 - (this.f_m(results) / results.length);
      return s;
    },

    f_m(results) {
      let result = this.mode(results);
      let count = 0;
      results.forEach(val => {
        if (val === result) {
          count++;
        }
      });
      return count;
    },

    mode(results) {
      let frequency = {};
      results.forEach(val => frequency[val] = (frequency[val] || 0) + 1);
      let max = 0;
      let result;
      for (const key in frequency) {
        if (frequency[key] > max) {
          max = frequency[key];
          result = key;
        }
      }
      return result;
    },

    async getPrompt(input) {
      const template = 'SENTENCE: {sentence}\nQUESTION: Is this (0) unacceptable, or (1) acceptable?\nANSWER:'
      const prompt = new PromptTemplate({
        template: template,
        inputVariables: ["sentence"]
      });
      let formattedPrompt = await prompt.format({
        sentence: input
      });
      return template + formattedPrompt;
    },

    getDatasets() {
      let requireComponent = require.context('../../perturbed_datasets', false, /[a-z0-9]+\.json$/)
      this.datasets = Object.assign({}, ...requireComponent.keys().map(fileName => ({
        [fileName.substr(2, fileName.length - 7)]: requireComponent(fileName)
      })))
      this.datasetNameList = Object.keys(this.datasets)
    },

    getExamples() {
      let selectedDataset = this.datasets[this.selectedDatasetName]
      for (let i = 0; i < this.exampleNumber; i++) {
        this.currentExamples.push(selectedDataset[i])
      }
    },

    fetchModels() {
      fetch("https://api.openai.com/v1/models", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.openAIApiKey}`,
        },
      })
        .then((res) => res.json())
        .then((data) => {
          this.modelList = data.data
          // .filter(
          //   (model) =>
          //     model.id.startsWith("gpt") &&
          //     model.owned_by === "openai" &&
          //     !model.id.includes("curie")
          // );
        });
    },
  },

  watch: {
    'modelConfig.temperature': {
      /* eslint-disable no-unused-vars */
      async handler(newTemperature, oldTemperature) {
        this.modelConfig.temperature = parseFloat(newTemperature);
        // this.modelConfig.llm.temperature = this.modelConfig.temperature;
      }
    },

    'modelConfig.top_p': {
      /* eslint-disable no-unused-vars */
      async handler(newTopP, oldTopP) {
        this.modelConfig.top_p = parseFloat(newTopP);
        // this.modelConfig.llm.top_p = this.modelConfig.top_p;
      }
    },

    'modelConfig.maxTokens': {
      /* eslint-disable no-unused-vars */
      async handler(newMaxTokens, oldMaxTokens) {
        this.modelConfig.maxTokens = parseInt(newMaxTokens);
        this.modelConfig.llm.maxTokens = this.modelConfig.maxTokens;
      }
    },

    'modelConfig.selectedModel': {
      /* eslint-disable no-unused-vars */
      async handler(newModel, oldModel) {
        this.modelConfig.selectedModel = newModel;
        this.showResults = false;
        await this.initModel();
      }
    },

    'showSuccessToast': {
      /* eslint-disable no-unused-vars */
      async handler(newShowSuccessToast, oldShowSuccessToast) {
        if (newShowSuccessToast) {
          setTimeout(() => {
            this.showSuccessToast = false;
          }, 2000);
        }
      }
    },

    // 'errorToast.show':{
    //   /* eslint-disable no-unused-vars */
    //   async handler(newErrorToastShow, oldErrorToastShow) {
    //     if (newErrorToastShow) {
    //       setTimeout(() => {
    //         this.errorToast.show = false;
    //       }, 3000);
    //     }
    //   }
    // }
  },

};
</script>