<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
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
                            <label for="selectedModel" class="form-label">Chat Model</label>
                            <select v-model="chatConfig.selectedModel" class="form-select" id="selectedModel">
                              <option v-for="model in chatModelList" :key="model.id" :value="model.id">
                                {{ model.id }}
                              </option>
                            </select>
                          </div>

                          <hr />

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
                            <textarea v-autosize class="form-control" id="systemPrompt"
                              v-model="chatConfig.systemPrompt" />
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
                          <div v-for="(item, index) in chatConfig.tools" :key="index" class="form-check">
                            <input class="form-check-input" type="checkbox" value="" :id="'flexCheckChecked' + index"
                              v-model="item.checked">
                            <label class="form-check-label" :for="'flexCheckChecked' + index">
                              {{ item.name }}
                            </label>
                          </div>
                          <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="" :id="'addNewToolId'" v-model="addingNewTool">
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
                                <input type="text" class="form-control" id="toolDescription" v-model="newTool.description" value="A search engine. Useful for when you need to answer questions about current events. Input should be a search query.">
                              </div>
                            </div>
                            <hr />
                            <div class="form-group row">
                              <label for="toolRegion" class="col-sm-3 col-form-label">Region</label>
                              <div class="col-sm-9">
                                <input type="text" class="form-control" id="toolRegion" v-model="newTool.region" value="eu-north-1">
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
                                <input type="text" class="form-control" id="toolSecretAccessKey" v-model="newTool.secretAccessKey">
                              </div>
                            </div>
                            <hr />
                            <div class="form-group row">
                              <label for="toolFunctionName" class="col-sm-3 col-form-label">Function Name</label>
                              <div class="col-sm-9">
                                <input type="text" class="form-control" id="toolFunctionName" v-model="newTool.functionName">
                              </div>
                            </div>
                            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                              <button class="btn btn-primary" type="button" @click.prevent="addNewTool">Save</button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </form>
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

                    <h1 class="display-4">Start a conversation</h1>
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
import Vue from "vue";
import {
  ChatPromptTemplate,
  HumanMessagePromptTemplate,
  SystemMessagePromptTemplate,
  MessagesPlaceholder,
} from "langchain/prompts";

export default {
  name: "prompting-view",
  components: {
    MessageView,
  },

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
    chatModelList: [],
    availableTools: [],
    addingNewTool: false,

    // TODO: remove the initial values. These are just for testing
    newTool: {
      name: 'Search1',
      description: 'A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
      region: 'eu-north-1',
      accessKeyId: '',
      secretAccessKey: '',
      functionName: 'my_random_function',
    },


    chatConfig: {
      chatMode: "normal_chat",
      selectedModel: "gpt-3.5-turbo",
      temperature: 0.7,
      maxTokens: 256,
      top_p: 0.9,
      systemPrompt: "The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.",
      tools: [],
    },

    oldTools: null,

    user: {
      name: "You",
      id: 2,
    },
  }),

  created() {
    this.messages = [];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    if (this.openAIApiKey != null) {
      this.initChatModel();
      this.fetchModels();
    }
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
        this.availableTools.push({
          name: this.newTool.name,
          description: this.newTool.description,
          tool: lambdaFunction,
        });
        this.addingNewTool = false;
        this.oldTools = JSON.parse(JSON.stringify(this.chatConfig.tools));
        this.chatConfig.tools.push({
          name: this.newTool.name,
          checked: false,
        });
      }
    },
    
    async onSubmit() {
      if (this.chatText != "") {
        let text = this.chatText;
        this.chatText = "";
        this.messages.push({
          author: this.user.name,
          text,
          uid: this.user.id,
          isMine: true,
        });

        Vue.nextTick(() => {
          this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
        });

        try {
          if (this.openAIApiKey === "") {
            // TODO: show worning message about the key
          } else {
            const res = await this.chatModel.call({ input: text });
            let response = "";
            if (this.chatConfig.chatMode === "normal_chat") {
              response = res.response;
            } else {
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
            }

            console.log(response);

            this.messages.push({
              author: "AI",
              text: response,
              uid: 1,
              isMine: false,
            });

            Vue.nextTick(() => {
              this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
            });
          }
        } catch (err) {
          console.log(err.message);
          throw err;
          // if(err.response.data.error.code === "invalid_api_key"){
          //   // TODO: show error message about the key
          // }else{
          //   // TODO: show general error message
          // }
        }
      }
    },

    resetConv() {
      this.chatText = "";
      this.messages.splice(0, this.messages.length);
      this.chatModel.memory.clear();
    },

    saveKey() {
      localStorage.setItem("openAIApiKey", this.openAIApiKey);
      // TODO: show success message
    },

    async initChatModel() {
      // see ChatOpenAI class: https://api.python.langchain.com/en/latest/chat_models/langchain.chat_models.openai.ChatOpenAI.html#langchain.chat_models.openai.ChatOpenAI
      const chat = new ChatOpenAI({
        openAIApiKey: this.openAIApiKey,
        modelName: this.chatConfig.selectedModel,
        temperature: this.chatConfig.temperature,
        maxTokens: this.chatConfig.max_tokens,
        top_p: this.chatConfig.top_p,
      });

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
          return selectedTools.some((selectedTool) => selectedTool.name === tool.name);
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
          this.chatModelList = data.data.filter(
            (model) =>
              model.id.startsWith("gpt") &&
              model.owned_by === "openai" &&
              !model.id.includes("curie")
          );
        });
    },

    initTools() {
      this.availableTools = [
        {
          name: "Calculator",
          description: "A simple calculator that can add, subtract, multiply and divide numbers.",
          tool: new Calculator(),
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
      // });
    
      for (let i = 0; i < this.availableTools.length; i++) {
        const tool = this.availableTools[i];
        this.chatConfig.tools.push({
          name: tool.name,
          checked: false,
        });
      }
    }
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
      }
    },

    'chatConfig.systemPrompt':{
      /* eslint-disable no-unused-vars */
      // TODO: this is not working. Fix it
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
        this.oldTools = newTools; 
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
