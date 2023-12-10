<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <!-- Config -->
            <div class="col col-3 d-none d-md-block">
              <div style="height: 35rem; overflow-y: auto; overflow-x: hidden;">
                <div class="form-group pb-2">
                  <div class="form-group">
                    <label for="selectedModel" class="form-label">Chat Model</label>
                    <select v-model="chatConfig.selectedModel" class="form-select" id="selectedModel">
                      <option v-for="model in localChatModels.concat(openAIChatModels)" :key="model" :value="model">
                        {{ model }}
                      </option>
                    </select>
                  </div>

                  <div v-if="openAIChatModels.includes(chatConfig.selectedModel)" class="row mt-3">
                    <div>
                      <label for="open-ai-key" class="form-label">
                        OpenAI key
                        <ToolTip 
                          content="Rest assured, your API keys are never stored on our end. They will always remain securely in the local storage of your computer.">
                        </ToolTip>
                      </label>
                      <input type="password" class="form-control" id="open-ai-key" placeholder="OpenAI key"
                        v-model="openAIApiKey" />
                    </div>
                  </div>
                  <hr />
                </div>
                <div class="form-group">
                  <label for="chat-mode" class="form-label">Mode</label>
                  <div class="list-group" id="chat-mode">
                    <a href="#" class="list-group-item list-group-item-action" v-on:click.prevent="chatConfig.chatMode = 'normal_chat'" :class="{'active': chatConfig.chatMode == 'normal_chat'}">Normal Chat</a>
                    <a href="#" class="list-group-item list-group-item-action" v-on:click.prevent="chatConfig.chatMode = 'agent_chat'" :class="{'active': chatConfig.chatMode == 'agent_chat'}">Agent Chat</a>
                    <a href="#" class="list-group-item list-group-item-action" v-on:click.prevent="chatConfig.chatMode = 'sensitivity'" :class="{'active': chatConfig.chatMode == 'sensitivity'}">Sensitivity</a>
                  </div>
                </div>
                <hr />
                <div class="form-group mb-3" v-if="chatConfig.chatMode === 'sensitivity'">
                  <label for="selectedDataset" class="form-label">Dataset (to show examples form)</label>
                  <select v-model="selectedDatasetName" class="form-select" id="selectedDataset">
                    <option v-for="datasetName in datasetNameList" :key="datasetName" :value="datasetName">
                      {{ datasetName }}
                    </option>
                  </select>
                </div>
                <div class="accordion" id="chatControl">
                  <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                        Controls
                      </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne"
                      data-bs-parent="#chatControl">
                      <div class="accordion-body">
                        <div class="form-group">
                          <label for="tempRange" class="form-label">Tempreture: {{ this.chatConfig.temperature
                          }}</label>
                          <input v-model="chatConfig.temperature" type="range" class="form-range" min="0" max="1"
                            step="0.1" id="tempRange">
                        </div>
                        <hr />
                        <div class="form-group">

                          <label for="maxTokens" class="form-label">Max Tokens</label>
                          <input type="number" class="form-control" id="maxTokens" min="0" max="32768"
                            v-model="chatConfig.maxTokens" />
                        </div>
                        <hr />
                        <div class="form-group">
                          <label for="top_pRange" class="form-label">top_p: {{ this.chatConfig.top_p }}</label>
                          <input v-model="chatConfig.top_p" type="range" class="form-range" min="0" max="1" step="0.1"
                            id="top_pRange">
                        </div>
                        <hr class="form-group" v-if="['normal_chat'].includes(chatConfig.chatMode)" />
                        <div class="form-group" v-if="['normal_chat'].includes(chatConfig.chatMode)">
                          <label for="systemPrompt" class="form-label">System Prompt</label>
                          <textarea v-if="chatConfig.chatMode === 'normal_chat'" v-autosize class="form-control" id="systemPrompt" v-model="chatConfig.systemPrompt" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- Tools Configuration -->
                  <div class="accordion-item" v-if="chatConfig.chatMode === 'agent_chat'">
                    <h2 class="accordion-header" id="headingTwo">
                      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        data-bs-target="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">
                        Tools (AWS Lambda Functions)
                      </button>
                    </h2>
                    <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo"
                      data-bs-parent="#chatControl">
                      <div class="accordion-body">

                        <div class="d-flex justify-content-between align-items-center form-check"
                          v-for="(item, index) in chatConfig.tools" :key="index">
                          <div>
                            <input class="form-check-input" type="checkbox" :id="'flexCheckChecked' + index"
                              v-model="item.checked">
                            <label class="form-check-label" :for="'flexCheckChecked' + index"> {{ item.name }} </label>
                          </div>
                          <div v-if="index >= initialToolsNumber">
                            <button type="button" class="btn btn-sm btn-outline-danger" @click="deleteTool(item, index)">
                              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="currentColor"
                                class="bi bi-trash-fill" viewBox="0 0 16 16">
                                <path
                                  d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z">
                                </path>
                              </svg>
                            </button>
                          </div>
                        </div>
                        <div class="form-check">
                          <input class="form-check-input" type="checkbox" value="" :id="'addNewToolId'"
                            v-model="addingNewTool">
                          <label class="form-check-label" :for="'addNewToolId'">Add New Tool (Lambda Function)</label>
                        </div>
                        <div v-if="addingNewTool">
                          <br />
                          <div class="form-group row">
                            <label for="toolName" class="col-sm-3 col-form-label">Name</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolName" v-model="newTool.name">
                            </div>
                          </div>
                          <hr />
                          <div class="form-group row">
                            <label for="toolDescription" class="col-sm-3 col-form-label">Description</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolDescription" v-model="newTool.description"
                                value="A search engine. Useful for when you need to answer questions about current events. Input should be a search query.">
                            </div>
                          </div>
                          <hr />
                          <div class="form-group row">
                            <label for="toolRegion" class="col-sm-3 col-form-label">Region</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolRegion" v-model="newTool.region"
                                value="eu-north-1">
                            </div>
                          </div>
                          <hr />
                          <div class="form-group row">
                            <label for="toolAccessKeyId" class="col-sm-3 col-form-label">Access Key Id</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolAccessKeyId" v-model="newTool.accessKeyId">
                            </div>
                          </div>
                          <hr />
                          <div class="form-group row">
                            <label for="toolSecretAccessKey" class="col-sm-3 col-form-label">Secret Access Key</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolSecretAccessKey"
                                v-model="newTool.secretAccessKey">
                            </div>
                          </div>
                          <hr />
                          <div class="form-group row">
                            <label for="toolFunctionName" class="col-sm-3 col-form-label">Function Name</label>
                            <div class="col-sm-9">
                              <input type="text" class="form-control" id="toolFunctionName"
                                v-model="newTool.functionName">
                            </div>
                          </div>
                          <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <button class="btn btn-primary" type="button" @click.prevent="addNewTool">Save (locally in
                              the browser)</button>
                          </div>
                          <div v-if="addNewToolErrorMessage" class="alert mt-2 alert-danger text-center">
                            {{ addNewToolErrorMessage }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Messages View -->
            <div 
              class="col col-md-9 border rounded p-3 bg-white" 
              style="height: 77vh" 
              v-if="['normal_chat', 'agent_chat'].includes(chatConfig.chatMode)">
              <div style="height: 100%; flex-direction: column; display: flex">
                <div ref="messages" class="messages" style="flex-grow: 1; overflow: auto; padding: 1rem">
                  <MessageView v-for="message in messages" :key="message.id"
                    :class="['message', { right: message.isMine }]" :dark="message.isMine" :text="message.text"
                    :author="message.author" />
                </div>

                <div v-if="messages.length === 0" class="d-flex justify-content-center" style="flex-grow: 1">
                  <div class="text-center opacity-50 unselectable">

                    <!-- add h1 with that is a little transparent -->

                    <h1 class="display-4">Start a conversation!</h1>
                    <p class="lead">
                      Start a conversation with the AI by typing in the box
                      below.
                    </p>
                  </div>
                </div>

                <div class="mt-3">
                  <form>
                    <div class="row">
                      <div class="col-2 px-0 d-flex align-items-end justify-content-end">
                        <button :disabled="messages.length === 1" type="button" @click="resetConv"
                          class="btn btn-primary border rounded-5">
                          Reset
                        </button>
                      </div>
                      <div class="col-8">
                        <textarea v-autosize ref="textAreaRef" v-model="chatText" placeholder="Write a message"
                          type="text" class="form-control border p-2 m-0 auto-resize" style="
                            background: rgba(0, 0, 0, 0.1);
                            max-height: 40vh;
                            height: 2.5rem;
                            min-height: 2.5rem;"
                          @keydown.enter="handleEnterKey" />
                      </div>
                      <div class="col-2 px-0 d-flex align-items-end">
                        <button @click.prevent="onSubmit" 
                        :disabled="chatText === ''" 
                        class="btn btn-danger text-white">
                          Send
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            </div>
            <!-- Sensitivity -->
            <div class="col col-md-9 rounded" v-else>
              <form class="form" @submit.prevent="getSensitivity">

                <!-- System Prompt + Examples -->
                <div class="me-auto mt-4 mt-md-0">
                  <div class="bg-light border border-primary rounded h-100 p-3">
                    <div class="w-100">
                      <label for="sensitivityPromptTemplate" class="form-label">
                        1. Prompt Template 
                        <ToolTip 
                          content="Your template for the prompt must include the placeholder {sentence} and {answer}. 
                          These placeholders will be replaced with actual sentences (and answers in case of few show examples) when prompting the model.">
                        </ToolTip>
                      </label>
                      <textarea v-autosize class="form-control" id="sensitivityPromptTemplate" v-model="chatConfig.sensitivityPromptTemplate" required/>
                      <div class="form-inline mt-3">
                        <label for="fewShotExamples" class="form-label">2. Enter your few shot examples</label>
                        <div class="row g-0" v-for="(choice, index) in listFewShotExamples" :key="index" id="fewShotExamples">
                          <div class="col col-9">
                            <div class="input-group input-group-sm mb-3">
                              <span class="input-group-text" id="basic-addon1">{{ index + 1 }}</span>
                              <input placeholder="SENTENCE" v-model="listFewShotExamples[index].sentence" type="text" class="form-control form-control-sm" required>
                            </div>
                          </div>
                          <div class="col col-3">
                            <div class="input-group input-group-sm mb-3 ps-2">
                              <input placeholder="ANSWER" v-model="listFewShotExamples[index].answer" type="text" class="form-control form-control-sm" required>
                            </div>
                          </div>
                        </div>
                        <div class="form-inline">
                          <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addFewShotExample">Add Example</button>
                          <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeFewShotExample">Remove Example</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Original Input -->
                <div class="me-auto mt-4 pt-3 mt-md-0">
                  <div class="bg-light border border-primary rounded h-100 p-3">
                    <div class="w-100">
                      <label for="originalInput" class="form-label">2. Enter your original input</label>
                      <textarea v-model="currentOriginalInput" @keydown.enter.exact.prevent
                        class="form-control form-control mb-2" style="resize: none; height: calc(40px);"
                        id="originalInput" placeholder="original input" required />
                      <p v-if="currentExamples.length > 0" class="form-label">Or try one of these examples</p>
                      <span role="button" v-for="(example, index) in currentExamples" :key="index"
                        v-on:click="selectExample(example)" class="badge bg-success m-1 text-wrap lh-base">{{
                          example.original
                        }}</span>
                    </div>
                  </div>
                </div>

                <!-- Perturbed Input -->
                <div class="me-auto mt-4 pt-3 mt-md-0">
                  <div class="bg-light border border-secondary rounded h-100 p-3">
                    <div class="w-100">
                      <div class="row">
                        <label for="perturbed_loop" class="form-label">3. Enter your perturbed input</label>
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
    <!-- <div class="position-fixed bottom-0 d-flex justify-content-center w-100 p-3">
      <div id="toastBootstrap" class="toast text-white bg-primary border-0" role="alert" aria-live="assertive"
        aria-atomic="true" v-bind:class="{ show: showSuccessToast }">
        <div class="d-flex">
          <div class="toast-body">
            Key was saved successfully.
          </div>
        </div>
      </div>
    </div> -->
    <div class="position-fixed bottom-0 d-flex justify-content-center w-100 p-3">
      <div id="toastBootstrapError" class="toast text-white bg-danger border-0" role="alert" aria-live="assertive"
        aria-atomic="true" v-bind:class="{ show: errorToast.show }">
        <div class="d-flex">
          <div class="toast-body">
            {{ errorToast.message }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="showResults" class="bg-light border rounded shadow p-3 mt-4">
      <div class="w-100">
        <div class="mb-1">
          <div class="container-fluid">
            <h1>
              Model {{ chatConfig.selectedModel }} has a sensitivity of {{ currentModelSensitivity }}.
            </h1>
            <hr/>
            <div class="row">
              <div class="col-7"></div>
              <div class="col-3 h5"> Actual Answer </div>
              <div class="col-2 h5"> Interpreted As </div>
            <div class="row"></div>
              <div class="col-7 h5 mb-4"> 
                &bull; Original Input: {{ currentOriginalInput }}
              </div>
              <div class="col-3" style="overflow-x: auto; white-space: nowrap;"> 
                {{ currentModelSensitivityResults[0].result }} 
              </div>
              <div class="col-2" > 
                {{ currentModelSensitivityResults[0].numResult ? 'acceptable': 'unacceptable' }}                 
              </div>
            </div>
              <div class="row mb-3" v-for="(text, index) in listHighlightedPerturbedInput" :key="index" id="perturbed_result">
                <div class="col-7">
                  <span class="h5" v-html="(index+1) + '. ' + text"></span>
                </div>
                <div class="col-3" style="overflow-x: auto; white-space: nowrap;"> 
                  {{ currentModelSensitivityResults[index+1].result }} 
                </div>
                <div class="col-2" > 
                  {{ currentModelSensitivityResults[index+1].numResult ? 'acceptable': 'unacceptable' }}                 
                </div>
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MessageView from "@/components/MessageView";
import ToolTip from "@/components/ToolTip";
import { BufferMemory } from "langchain/memory";
import { ConversationChain } from "langchain/chains";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { OpenAI } from "langchain/llms/openai";
import { Calculator } from "langchain/tools/calculator";
import { initializeAgentExecutorWithOptions } from "langchain/agents";
import { AWSLambda } from "langchain/tools/aws_lambda";
import { v4 as uuidv4 } from "uuid";
import Vue from "vue";
import {
  ChatPromptTemplate,
  HumanMessagePromptTemplate,
  SystemMessagePromptTemplate,
  MessagesPlaceholder,
  PromptTemplate,
  FewShotPromptTemplate,
} from "langchain/prompts";
import VueTippy from "vue-tippy";
import { 
  getOpenAIModels,
  getLocalLLMs 
} from '@/api';
import { CustomChatModel, CustomGenerativeModel } from "../services/custom_llm";

Vue.use(VueTippy);

export default {
  name: "prompting-view",
  components: {
    MessageView,
    ToolTip,
  },

  // to change the size of the textarea dynamically
  directives: {
    autosize: {
      bind: function (el) {
        let computed = window.getComputedStyle(el);
        el.style.height = "auto";
        el.style.overflowY = "auto";
        el.style.minHeight = computed.getPropertyValue("min-height");
        el.oninput = function () {
          el.style.height = "auto";
          el.style.height = el.scrollHeight + "px";
        }
      },
      inserted: function (el) {
        el.oninput();
      },
      componentUpdated: function (el, binding, vnode) {
        vnode.context.$nextTick(function () {
          el.oninput();
        });
      }
    }
  },

  data: () => ({
    chatModel: null,
    chatText: "",
    messages: [],
    openAIApiKey: "",
    openAIChatModels: [
      "gpt-3.5-turbo-16k-0613",
      "gpt-3.5-turbo-0613",
      "gpt-3.5-turbo",
      "gpt-3.5-turbo-0301",
    ],
    localChatModels: [
    "Llama-2-7b-chat",
    ],
    availableTools: [],
    addingNewTool: false,
    initialToolsNumber: 0,
    abortController: new AbortController(),

    newTool: {
      name: 'Search',
      description: 'A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
      region: 'eu-north-1',
      accessKeyId: '',
      secretAccessKey: '',
      functionName: 'my_random_function',
    },

    chatConfig: {
      chatMode: "sensitivity",
      selectedModel: "Llama-2-7b-chat",
      temperature: 0.7,
      maxTokens: 256,
      top_p: 0.9,
      systemPrompt: ``, 
      tools: [],
      sensitivityPromptTemplate: 'SENTENCE: {sentence}\nQUESTION: Is this (0) unacceptable, or (1) acceptable?\nANSWER: {answer}',
    },

    oldTools: null,
    addNewToolErrorMessage: null,
    // showSuccessToast: false,
    errorToast: {
      show: false,
      message: "",
    },

    user: {
      name: "You",
      id: 2,
    },

    generativeModel: null,
    currentModelSensitivity: 0,
    // showSuccessToast: false,
    currentOriginalInput: "",
    currentExamples: [],
    listPerturbedInput: ["", "", "", "", ""],
    waiting: false,
    selectedDatasetName: "cola",
    datasetNameList: [],
    datasets: {},
    exampleNumber: 3,
    showResults: false,
    currentModelSensitivityResults: [],
    listFewShotExamples: [{
      sentence: 'The sailors rode the breeze clear of the rocks.', 
      answer: '1'
    }, {
      sentence: 'The weights made the rope stretch over the pulley.',
      answer: '1'
    }, {
      sentence: 'The mechanical doll next itself loose.', 
      answer: '0'
    }]
  }),

  created() {
    this.messages = [];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    this.fetchModels();
    this.initChatModel();
    this.initGenerativeModel()
    this.initTools();
    this.getDatasets();
    this.getExamples();
  },

  computed: {
    listHighlightedPerturbedInput: function(){
      if (this.listPerturbedInput.length === 0 || this.currentOriginalInput === "") return [];

      const escapeHtml = (unsafe) => unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

      const tokenize = (sentence) => {
        const result = sentence.match(/\S+/g);
        return result ? result : [];
      }

      const highlight = (token) => `<mark class="bg-danger text-white">${escapeHtml(token)}</mark>`;

      const findDifferences = (originalTokens, perturbedTokens) => {
        let indexOriginal = 0;

        if (originalTokens.length === perturbedTokens.length){ // there is a token changed, highlight the changed token
          return perturbedTokens.map(perturbedToken => {
            let tokenToReturn = perturbedToken === originalTokens[indexOriginal] ? perturbedToken : highlight(perturbedToken);
            indexOriginal++;
            return tokenToReturn;
          }).join(" ");
        } else if (originalTokens.length < perturbedTokens.length){ // there is a token added, highlight the added token
          return perturbedTokens.map(perturbedToken => {
            let tokenToReturn = originalTokens.includes(perturbedToken) ? perturbedToken : highlight(perturbedToken);
            return tokenToReturn;
          }).join(" ");
        } else { // there is a token removed 
          return perturbedTokens.join(" "); // there is nothing to highlight
        }
      };

      const originalTokens = tokenize(this.currentOriginalInput);
      return this.listPerturbedInput.map(sentence => {
        const perturbedTokens = tokenize(sentence);
        return findDifferences(originalTokens, perturbedTokens);
      });
    }
  },

  methods: {

    addFewShotExample() {
      this.listFewShotExamples.push({
        sentence: '', 
        answer: ''
      });
    },

    removeFewShotExample() {
      this.listFewShotExamples.pop();
    },

    handleEnterKey (event) {
      if (event.shiftKey) {
        return; // If Shift+Enter is pressed, do the default action (add a newline)
      }
      event.preventDefault();
      this.onSubmit();
    },

    selectExample(example) {
      this.showResults = false;
      this.currentOriginalInput = example.original;
      for (let i = 0; i < this.listPerturbedInput.length; i++) {
        this.listPerturbedInput[i] = Object.entries(example.synthetic)[i][1]
      }
    },

    addChoice() {
      this.listPerturbedInput.push("");
      this.showResults = false;
    },

    removeChoice() {
      if(this.listPerturbedInput.length > 1){
        this.listPerturbedInput.pop();
        this.showResults = false;
      }
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
      return parseInt(result);
    },

    validateSensitivityTemplate(template) {
      return template.includes('{sentence}') && template.includes('{answer}');
    },

    async getPrompt(input) {
      if (!this.validateSensitivityTemplate(this.chatConfig.sensitivityPromptTemplate)) {
        throw new Error("Your template for the system prompt must include the placeholders {sentence} and {answer}.");
      }

      const promptTemplate = new PromptTemplate({
        template: this.chatConfig.sensitivityPromptTemplate,
        inputVariables: ["sentence", "answer"]
      });

      const fewShotPrompt = new FewShotPromptTemplate({
        suffix: this.chatConfig.sensitivityPromptTemplate, // template for the actual sentence, not the few shot examples
        prefix: 'Respond to the last question in the with the following format:', // telling the model what to do with the few shot examples
        examplePrompt: promptTemplate, // template for the few shot
        examples: this.listFewShotExamples,
        inputVariables: ["sentence", "answer"], // variables in the actual sentence template, not the few shot examples
      });
      
      let formattedPrompt = await fewShotPrompt.format({
        sentence: input,
        answer: ''
      });
      return formattedPrompt;
    },

    async getSensitivity() {
      this.waiting = true;
      this.showResults = false;
      if (this.selectedDatasetName === 'cola') {
        this.currentModelSensitivityResults = [];
        // get the result of the original input
        let prompt; 
        try{
          prompt = await this.getPrompt(this.currentOriginalInput);
        } catch (e) {
          console.error(e)
          this.errorToast.show = true;
          this.errorToast.message = e.message;
          this.waiting = false;
          return;
        }
        
        let res = await this.generativeModel.call(prompt);
        const results = []
        const numResult = res == 1 ? 1 : 0; // if the model returns anything other than 1 or 0, we assume it is 0
        this.currentModelSensitivityResults.push({
          result: res, 
          numResult: numResult
        });
        results.push(numResult);

        const promises = this.listPerturbedInput.map(async (input) => {
          const prompt = await this.getPrompt(input);
          const res = await this.generativeModel.call(prompt);
          const numResult = res == 1 ? 1 : 0;
          return {
            result: res,
            numResult: numResult
          };
        });

        const resultsArray = await Promise.all(promises);

        resultsArray.forEach(resultObj => {
          this.currentModelSensitivityResults.push(resultObj);
          results.push(resultObj.numResult);
        });

        console.log(results)
        this.currentModelSensitivity = this.calculateSensitivity(results);
        this.showResults = true;
      }
      this.waiting = false;
    },

    getExamples() {
      let selectedDataset = this.datasets[this.selectedDatasetName]
      for (let i = 0; i < this.exampleNumber; i++) {
        this.currentExamples.push(selectedDataset[i])
      }
    },

    getDatasets() {
      let requireComponent = require.context('../../perturbed_datasets', false, /[a-z0-9]+\.json$/)
      this.datasets = Object.assign({}, ...requireComponent.keys().map(fileName => ({
        [fileName.substr(2, fileName.length - 7)]: requireComponent(fileName)
      })))
      this.datasetNameList = Object.keys(this.datasets)
    },

    async initGenerativeModel() {
      if (this.localChatModels.includes(this.chatConfig.selectedModel)) {
        this.generativeModel = new CustomGenerativeModel({
          model_identifier: this.chatConfig.selectedModel,
          temperature: this.chatConfig.temperature,
          max_new_tokens: this.chatConfig.maxTokens,
          top_p: this.chatConfig.top_p,
          streaming: false,
        });
      }
      else if (this.openAIChatModels.includes(this.chatConfig.selectedModel)) {
        // see https://js.langchain.com/docs/modules/model_io/models/llms/integrations/openai
        this.generativeModel = new OpenAI({
          model: this.chatConfig.selectedModel,
          openAIApiKey: this.openAIApiKey,
          temperature: this.chatConfig.temperature,
          maxTokens: this.chatConfig.maxTokens,
          top_p: this.chatConfig.top_p,
        });
      }
    },

    async addNewTool() {
      if (this.newTool.name !== ''
        && this.newTool.description !== ''
        && this.newTool.region !== ''
        && this.newTool.accessKeyId !== ''
        && this.newTool.secretAccessKey !== ''
        && this.newTool.functionName !== '') {
        const lambdaFunction = new AWSLambda({
          name: this.newTool.name,
          description: this.newTool.description,
          region: this.newTool.region,
          accessKeyId: this.newTool.accessKeyId,
          secretAccessKey: this.newTool.secretAccessKey,
          functionName: this.newTool.functionName,
        });
        let toolId = uuidv4();
        this.availableTools.push({
          name: this.newTool.name,
          description: this.newTool.description,
          tool: lambdaFunction,
          toolId: toolId,
        });
        this.addingNewTool = false;
        this.oldTools = JSON.parse(JSON.stringify(this.chatConfig.tools));
        this.chatConfig.tools.push({
          name: this.newTool.name,
          checked: false,
          toolId: toolId,
        });
        this.saveToolLocally(toolId);
      } else {
        this.addNewToolErrorMessage = "All fields must be filled in.";
      }
    },

    saveToolLocally(toolId) {
      let localToolIds = localStorage.getItem("local_tool_ids");
      if (localToolIds == null) {
        localToolIds = [];
      } else {
        localToolIds = JSON.parse(localToolIds);
      }
      localToolIds.push(toolId);
      localStorage.setItem("local_tool_ids", JSON.stringify(localToolIds));
      let tool = this.availableTools[this.availableTools.length - 1];
      localStorage.setItem(`tool_${toolId}_name`, tool.name);
      localStorage.setItem(`tool_${toolId}_description`, tool.tool.description);
      localStorage.setItem(`tool_${toolId}_region`, tool.tool.lambdaConfig.region);
      localStorage.setItem(`tool_${toolId}_accessKeyId`, tool.tool.lambdaConfig.accessKeyId);
      localStorage.setItem(`tool_${toolId}_secretAccessKey`, tool.tool.lambdaConfig.secretAccessKey);
      localStorage.setItem(`tool_${toolId}_functionName`, tool.tool.lambdaConfig.functionName);
    },

    async deleteTool(tool, index) {
      localStorage.removeItem(`tool_${tool.toolId}_name`);
      localStorage.removeItem(`tool_${tool.toolId}_description`);
      localStorage.removeItem(`tool_${tool.toolId}_region`);
      localStorage.removeItem(`tool_${tool.toolId}_accessKeyId`);
      localStorage.removeItem(`tool_${tool.toolId}_secretAccessKey`);
      localStorage.removeItem(`tool_${tool.toolId}_functionName`);

      let localToolIds = localStorage.getItem("local_tool_ids");
      if (localToolIds == null) {
        localToolIds = [];
      } else {
        localToolIds = JSON.parse(localToolIds);
      }
      localToolIds = localToolIds.filter((id) => id !== tool.toolId);
      localStorage.setItem("local_tool_ids", JSON.stringify(localToolIds));

      this.availableTools.splice(index, 1);
      this.oldTools = JSON.parse(JSON.stringify(this.chatConfig.tools));

      // if the tool is checked, reset the conversation because tool is not available anymore
      if (this.chatConfig.tools[index].checked) {
        await this.initChatModel();
        this.initGenerativeModel();
        this.resetConv();
      }

      this.chatConfig.tools.splice(index, 1);
    },

    addUserMessage() {
      let text = this.chatText;
      this.messages.push({
        author: this.user.name.toUpperCase(),
        text,
        uid: this.user.id,
        isMine: true,
      });
      Vue.nextTick(() => {
        this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
      });
    },

    async onSubmit() {
      this.addUserMessage()
      let text = this.chatText;
      this.chatText = "";
      
      try {
        let response = "";
        if (this.openAIChatModels.includes(this.chatConfig.selectedModel) && this.openAIApiKey === ""){
          this.errorToast.message = "Please enter your OpenAI key first.";
          this.errorToast.show = true;
          return;
        }

        this.messages.push({
          author: this.chatConfig.selectedModel.toUpperCase(),
          text: "",
          uid: 1,
          isMine: false,
        });

        this.abortController = new AbortController();
        if (this.chatConfig.chatMode === "normal_chat") {
          const self = this;
          const res = await this.chatModel.call({ 
            input: text, 
            signal: this.abortController.signal,
            callbacks: [
              {
                handleLLMNewToken: (token) => {
                  this.messages[this.messages.length - 1].text += token;
                }
              }
            ]
          });
          response = res.response;
          console.log(response);
          Vue.nextTick(() => {
            self.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
          });
        // TODO: make this stream too 
        } else { // agent chat
          const res = await this.chatModel.call({ input: text });
          if (res.intermediateSteps.length > 0) {
            response += "```\n";
            for (let i = 0; i < res.intermediateSteps.length; i++) {
              const step = res.intermediateSteps[i];
              console.log(step);
              response += `Action [${i + 1}] tool:\t ${step.action.tool
                } \n`;
              response += `Action [${i + 1}] Input:\t ${step.action.toolInput
                } \n`;
              response += `Action [${i + 1}] Output:\t ${step.observation
                } \n`;
              response +=
                "============================================== \n";
            }
            response += "```\n";
            response += "Final Answer: " + res.output;
          } else {
            response = res.output;
          }
          this.messages[this.messages.length - 1].text = response;
        }
        
      } catch (err) {
        console.error(err.message);
        if (err.response && err.response.data && err.response.data.error.code === "invalid_api_key") {
          this.errorToast.message = "Please enter a valid OpenAI key.";
          this.errorToast.show = true;
        }else if(err.message === "AbortError"){
          console.log("Request aborted")
        } else {
          this.errorToast.message = "Something went wrong. Please try again."
          this.errorToast.show = true;
        }
      }
    },

    resetConv() {
      this.abortController.abort();
      this.chatText = "";
      this.messages.splice(0, this.messages.length);
      this.chatModel?.memory.clear();
    },

    async initChatModel() {
      let chat = null;

      if (this.localChatModels.includes(this.chatConfig.selectedModel)) {
        chat = new CustomChatModel({
          model_identifier: this.chatConfig.selectedModel,
          temperature: this.chatConfig.temperature,
          max_new_tokens: this.chatConfig.maxTokens,
          top_p: this.chatConfig.top_p,
          streaming: true,
        });
      }
      else if (this.openAIChatModels.includes(this.chatConfig.selectedModel)) {
        chat = new ChatOpenAI({
          openAIApiKey: this.openAIApiKey,
          modelName: this.chatConfig.selectedModel,
          temperature: this.chatConfig.temperature,
          maxTokens: this.chatConfig.maxTokens,
          top_p: this.chatConfig.top_p,
          streaming: true, 
        });
      }

      if (chat !== null) {
        const chatPrompt = ChatPromptTemplate.fromPromptMessages([
          SystemMessagePromptTemplate.fromTemplate(this.chatConfig.systemPrompt),
          new MessagesPlaceholder("chat_history"),
          HumanMessagePromptTemplate.fromTemplate("{input}"),
        ]);

        const memory = new BufferMemory({ returnMessages: true, memoryKey: "chat_history" });

        if (this.chatConfig.chatMode === "normal_chat") {

          this.chatModel = new ConversationChain({
            memory: memory,
            llm: chat,
            prompt: chatPrompt,
          });

        } else if (this.chatConfig.chatMode === "agent_chat") {
          process.env.LANGCHAIN_HANDLER = "langchain";

          // filter the tools that are checked
          const selectedTools = this.chatConfig.tools.filter((tool) => tool.checked);

          const actualTools = this.availableTools.filter((tool) => {
            return selectedTools.some((selectedTool) => selectedTool.toolId === tool.toolId);
          }).map((tool) => tool.tool);

          this.chatModel = await initializeAgentExecutorWithOptions(
            actualTools,
            chat,
            {
              agentType: "chat-conversational-react-description", // automatically creates and uses BufferMemory with the executor.
              returnIntermediateSteps: true,
              verbose: true,
            },
          );
        }
      }

    },

    async fetchModels() {
      if (this.openAIApiKey !== "") {
        let response = await getOpenAIModels(this.openAIApiKey);
        this.openAIChatModels = response.data.data.filter(
          (model) =>{
            if (this.chatConfig.chatMode !== "sensitivity"){
              return model.id.startsWith("gpt") &&
              !model.id.includes("curie")
            } else {
              return (model.id.startsWith("gpt") || model.id.startsWith("text") || model.id.startsWith("davinci")) && 
              !model.id.includes("curie")
            }
          }
        ).map((model) => model.id);
      }

      let response = await getLocalLLMs();
      this.localChatModels = response.data.filter(
        (model) => 
          model.model_type === "llm"
      ).map((model) => model.identifier);
      this.localChatModels.push("Llama-2-7b-chat"); // TODO: remove when models are available in production
    },

    initTools() {
      this.availableTools = [
        {
          name: "Calculator",
          description: "A simple calculator that can add, subtract, multiply and divide numbers.",
          tool: new Calculator(),
          toolId: 1,
        }
      ];

      // const searchLambdaFunction = new AWSLambda({
      //   name: 'Search',
      //   description: 'A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
      //   region: 'eu-north-1',
      //   accessKeyId: process.env.VUE_APP_AWS_ACCESS_KEY_ID,
      //   secretAccessKey: process.env.VUE_APP_AWS_SECRET_ACCESS_KEY,
      //   functionName: 'my_random_function',
      // });

      // this.availableTools.push({
      //   name: "Search",
      //   description: "A search engine. Useful for when you need to answer questions about current events. Input should be a search query.",
      //   tool: searchLambdaFunction,
      //   toolId: 2,
      // });

      // add any initial tools before this line
      this.initialToolsNumber = this.availableTools.length;

      // get tools from local storage
      const localToolIds = localStorage.getItem("local_tool_ids");

      if (localToolIds != null) {
        const localToolIdsList = JSON.parse(localToolIds);
        for (let i = 0; i < localToolIdsList.length; i++) {
          const toolId = localToolIdsList[i];
          const tool = {
            name: localStorage.getItem(`tool_${toolId}_name`),
            description: localStorage.getItem(`tool_${toolId}_description`),
            tool: new AWSLambda({
              name: localStorage.getItem(`tool_${toolId}_name`),
              description: localStorage.getItem(`tool_${toolId}_description`),
              region: localStorage.getItem(`tool_${toolId}_region`),
              accessKeyId: localStorage.getItem(`tool_${toolId}_accessKeyId`),
              secretAccessKey: localStorage.getItem(`tool_${toolId}_secretAccessKey`),
              functionName: localStorage.getItem(`tool_${toolId}_functionName`),
            }),
            toolId: toolId,
          };
          this.availableTools.push(tool);
        }
      }
      for (let i = 0; i < this.availableTools.length; i++) {
        const tool = this.availableTools[i];
        this.chatConfig.tools.push({
          name: tool.name,
          checked: false,
          toolId: tool.toolId,
        });
      }
    },
  },

  watch: {
    'chatConfig.temperature': {
      /* eslint-disable no-unused-vars */
      async handler(newTemperature, oldTemperature) {
        this.chatConfig.temperature = parseFloat(newTemperature);
        this.chatModel.llm.temperature = this.chatConfig.temperature;
      }
    },

    'chatConfig.top_p': {
      /* eslint-disable no-unused-vars */
      async handler(newTopP, oldTopP) {
        this.chatConfig.top_p = parseFloat(newTopP);
        this.chatModel.llm.top_p = this.chatConfig.top_p;
      }
    },

    'chatConfig.maxTokens': {
      /* eslint-disable no-unused-vars */
      async handler(newMaxTokens, oldMaxTokens) {
        this.chatConfig.maxTokens = parseInt(newMaxTokens);
        this.chatModel.llm.maxTokens = this.chatConfig.maxTokens;
        this.chatModel.llm.max_new_tokens = this.chatConfig.maxTokens;
      }
    },

    'chatConfig.systemPrompt': {
      /* eslint-disable no-unused-vars */
      async handler(newSystemPrompt, oldSystemPrompt) {
        this.chatConfig.systemPrompt = newSystemPrompt;
        this.chatModel.prompt.promptMessages[0] = SystemMessagePromptTemplate.fromTemplate(this.chatConfig.systemPrompt);
      }
    },

    'chatConfig.selectedModel': {
      /* eslint-disable no-unused-vars */
      async handler(newModel, oldModel) {
        this.showResults = false;
        this.chatConfig.selectedModel = newModel;
        await this.initChatModel();
        this.initGenerativeModel();
        this.resetConv();
      }
    },

    'chatConfig.chatMode': {
      /* eslint-disable no-unused-vars */
      async handler(newChatMode, oldChatMode) {
        this.showResults = false;
        this.chatConfig.chatMode = newChatMode;
        await this.fetchModels();
        await this.initChatModel();
        this.initGenerativeModel();
        this.resetConv();
      }
    },

    'chatConfig.tools': {
      deep: true,
      async handler(newTools) {
        if (this.oldTools && newTools.length === this.oldTools.length) {
          await this.initChatModel();
          this.initGenerativeModel();
          this.resetConv();
        }
        this.oldTools = JSON.parse(JSON.stringify(newTools));
      }
    },

    // 'showSuccessToast': {
    //   /* eslint-disable no-unused-vars */
    //   async handler(newShowSuccessToast, oldShowSuccessToast) {
    //     if (newShowSuccessToast) {
    //       setTimeout(() => {
    //         this.showSuccessToast = false;
    //       }, 2000);
    //     }
    //   }
    // },

    'openAIApiKey': {
      /* eslint-disable no-unused-vars */
      async handler(newKey, oldKey) {
        localStorage.setItem("openAIApiKey", newKey);
        if (newKey !== "") {
          await this.fetchModels();
          await this.initChatModel();
          this.initGenerativeModel();
        }
      }
    },

    'errorToast.show': {
      /* eslint-disable no-unused-vars */
      async handler(newErrorToastShow, oldErrorToastShow) {
        if (newErrorToastShow) {
          setTimeout(() => {
            this.errorToast.show = false;
          }, 3000);
        }
      }
    }
  },

};
</script>

<style scoped>
.message+.message {
  margin-top: 1rem;
}

.message.right {
  margin-left: auto;
}

button:disabled {
  opacity: 0.5;
}

.unselectable {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera, and W3C */
}
</style>
