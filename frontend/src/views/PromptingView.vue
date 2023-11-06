<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <div class="col col-4 d-none d-md-block">
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
                        <svg
                          content="Rest assured, your API keys are never stored on our end. They will always remain securely in the local storage of your computer."
                          v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                          class="bi bi-info-circle" viewBox="0 0 16 16">
                          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                          <path
                            d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                        </svg>
                      </label>
                      <input type="password" class="form-control" id="open-ai-key" placeholder="OpenAI key"
                        v-model="openAIApiKey" />
                    </div>
                  </div>
                  <hr />
                </div>

                <div class="form-group">
                  <label for="chat-mode" class="form-label">Chat Mode</label>
                  <select v-model="chatConfig.chatMode" class="form-select" id="chat-mode">
                    <option value="normal_chat">Normal Chat</option>
                    <option value="agent_chat">Agent Chat</option>
                  </select>
                </div>

                <hr />

                <div class="accordion" id="chatControl">

                  <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                        Chat Controls
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

                        <hr class="form-group" v-if="chatConfig.chatMode === 'normal_chat'" />

                        <div class="form-group" v-if="chatConfig.chatMode === 'normal_chat'">
                          <label for="systemPrompt" class="form-label">System Prompt</label>
                          <textarea v-autosize class="form-control" id="systemPrompt" v-model="chatConfig.systemPrompt" />
                        </div>

                      </div>
                    </div>
                  </div>

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
            <div class="col col-md-8 border rounded p-3 bg-white" style="height: 77vh">
              <div style="height: 100%; flex-direction: column; display: flex">
                <div ref="messages" class="messages" style="flex-grow: 1; overflow: auto; padding: 1rem">
                  <MessageView v-for="message in messages" :key="message.id"
                    :class="['message', { right: message.isMine }]" :dark="message.isMine" :text="message.text"
                    :author="message.author" />
                </div>

                <div v-if="messages.length === 0" class="d-flex justify-content-center" style="flex-grow: 1">
                  <div class="text-center opacity-50">

                    <!-- add h1 with that is a little transparent -->

                    <h1 class="display-4">Start a conversation!</h1>
                    <p class="lead">
                      Start a conversation with the AI by typing in the box
                      below.
                    </p>
                  </div>
                </div>

                <div class="mt-3">
                  <form @submit.prevent="onSubmit">
                    <div class="row">
                      <div class="col-2 px-0 d-flex align-items-end justify-content-end">
                        <button :disabled="messages.length === 1" type="button" @click="resetConv"
                          class="btn btn-primary border rounded-5">
                          Reset
                        </button>
                      </div>
                      <div class="col-8">
                        <textarea v-autosize v-model="chatText" placeholder="Write a message" type="text"
                          class="form-control border-0 p-2 m-0 auto-resize" style="
                            background: rgba(0, 0, 0, 0.1);
                            max-height: 12rem;
                            height: 2rem;
                          " @keydown.enter.prevent="onSubmit" />
                      </div>
                      <div class="col-2 px-0 d-flex align-items-end">
                        <button :disabled="chatText === ''" class="btn btn-danger text-white">
                          Send
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
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
  </div>
</template>

<script>
import MessageView from "@/components/MessageView";
import { BufferMemory } from "langchain/memory";
import { ConversationChain } from "langchain/chains";
import { ChatOpenAI } from "langchain/chat_models/openai";
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
} from "langchain/prompts";
import VueTippy from "vue-tippy";
import { 
  getOpenAIModels,
  getLocalLLMs 
} from '@/api';
import CustomChatModel from "../services/custom_llm";

Vue.use(VueTippy);

export default {
  name: "prompting-view",
  components: {
    MessageView,
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
    localChatModels: [],
    availableTools: [],
    addingNewTool: false,
    initialToolsNumber: 0,

    newTool: {
      name: 'Search',
      description: 'A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
      region: 'eu-north-1',
      accessKeyId: '',
      secretAccessKey: '',
      functionName: 'my_random_function',
    },


    chatConfig: {
      chatMode: "normal_chat",
      selectedModel: "Llama-2-7b-chat",
      temperature: 0.7,
      maxTokens: 256,
      top_p: 0.9,
      systemPrompt: "The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.",
      tools: [],
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
  }),

  created() {
    this.messages = [];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    this.fetchModels();
    this.initChatModel();
    this.initTools();
  },

  methods: {
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

        if (this.chatConfig.chatMode === "normal_chat") {
          const self = this;

          if(this.localChatModels.includes(this.chatConfig.selectedModel)){
            // TODO: make this stream too
            const res = await this.chatModel.call({ input: text }); 
            response = res.response;
            this.messages[this.messages.length - 1].text = response;
          }else{ 
            await this.chatModel.call({
              input: text,
              callbacks: [
                {
                  handleLLMNewToken: (token) => {
                    this.messages[this.messages.length - 1].text += token;
                    Vue.nextTick(() => {
                      self.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
                    });
                    response += token;
                  }
                }
              ]
            });
          }
          console.log(response);
        }

        // TODO: make this stream too 
        else { // agent chat
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
        console.log(err.message);
        if (err.response.data.error.code === "invalid_api_key") {
          this.errorToast.message = "Please enter a valid OpenAI key.";
          this.errorToast.show = true;
        } else {
          this.errorToast.message = "Something went wrong. Please try again."
          this.errorToast.show = true;
        }
      }
    },

    resetConv() {
      this.chatText = "";
      this.messages.splice(0, this.messages.length);
      this.chatModel.memory.clear();
    },

    async initChatModel() {
      let chat = null;

      if (this.localChatModels.includes(this.chatConfig.selectedModel)) {
        chat = new CustomChatModel({
          model_identifier: this.chatConfig.selectedModel,
          temperature: this.chatConfig.temperature,
          max_new_tokens: this.chatConfig.maxTokens,
          top_p: this.chatConfig.top_p,
          streaming: false,
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
          (model) =>
            model.id.startsWith("gpt") &&
            model.owned_by === "openai" &&
            !model.id.includes("curie")
        ).map((model) => model.id);
      }

      let response = await getLocalLLMs();
      this.localChatModels = response.data.filter(
        (model) => 
          model.model_type === "llm"
      ).map((model) => model.identifier);
      this.localChatModels.push("Llama-2-7B-Chat-AWQ"); // TODO: remove when models are available in production
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
        this.chatConfig.selectedModel = newModel;
        await this.initChatModel();
        this.resetConv();
      }
    },

    'chatConfig.chatMode': {
      /* eslint-disable no-unused-vars */
      async handler(newChatMode, oldChatMode) {
        this.chatConfig.chatMode = newChatMode;
        await this.initChatModel();
        this.resetConv();
      }
    },

    'chatConfig.tools': {
      deep: true,
      async handler(newTools) {
        if (this.oldTools && newTools.length === this.oldTools.length) {
          await this.initChatModel();
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
</style>
