<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <div class="col col-3 d-none d-md-block">
              <form class="form-inline" @submit.prevent="saveKey">
                <div class="form-group pb-2">
                  <div class="row">
                    <div class="col-9">
                      <label for="open-ai-key"
                        >OpenAI key (locally stored)</label
                      >
                      <input
                        type="password"
                        class="form-control"
                        id="open-ai-key"
                        placeholder="OpenAI key"
                        title="Your key is stored locally and not shared with anyone"
                        v-model="openAIApiKey"
                      />
                    </div>
                    <div class="col-3 ps-0 d-flex align-items-end">
                      <button type="submit" class="btn btn-primary px-3">
                        Save
                      </button>
                    </div>
                  </div>

                  <div class="form-group">
                    <label for="selectedModel">Chat Model</label>
                    <select
                      v-model="selectedModel"
                      class="form-select"
                      id="selectedModel"
                    >
                      <option
                        v-for="model in chatModelList"
                        :key="model.id"
                        :value="model.id"
                      >
                        {{ model.id }}
                      </option>
                    </select>
                  </div>

                  <!-- <div class="row">
                    <div class="col-9">
                      <label for="open-ai-key" >Search key (locally stored)</label>
                      <input
                        type="password"
                        class="form-control"
                        id="search-key"
                        placeholder="Search Key"
                        title="Your key is stored locally and not shared with anyone"
                        v-model="searchKey"
                      />
                    </div>
                    <div class="col-3 ps-0 d-flex align-items-end">
                      <button
                        type="button"
                        @click="saveSearchKey"
                        class="btn btn-primary px-3"
                      >
                        Save
                      </button>
                    </div>
                  </div> -->
                </div>
                <div class="form-group">
                  <label for="chat-mode">Chat Mode</label>
                  <select v-model="chatMode" class="form-select" id="chat-mode">
                    <option value="normal_chat">Normal Chat</option>
                    <option value="agent_chat">Agent Chat</option>
                  </select>
                </div>
              </form>
            </div>
            <div
              class="col col-md-9 border rounded p-3 bg-white"
              style="height: 77vh"
            >
              <div style="height: 100%; flex-direction: column; display: flex">
                <div
                  ref="messages"
                  class="messages"
                  style="flex-grow: 1; overflow: auto; padding: 1rem"
                >
                  <MessageView
                    v-for="message in messages"
                    :key="message.id"
                    :class="['message', { right: message.isMine }]"
                    :dark="message.isMine"
                    :text="message.text"
                    :author="message.author"
                  />
                </div>

                <div
                  v-if="messages.length === 0"
                  class="d-flex justify-content-center"
                  style="flex-grow: 1"
                >
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
                      <div
                        class="col-2 px-0 d-flex align-items-end justify-content-end"
                      >
                        <button
                          :disabled="messages.length === 1"
                          type="button"
                          @click="resetConv"
                          class="btn btn-primary border rounded-5"
                        >
                          Reset
                        </button>
                      </div>
                      <div class="col-8">
                        <textarea
                          v-model="chatText"
                          placeholder="Write a message"
                          type="text"
                          class="form-control border-0 p-2 m-0 auto-resize"
                          style="
                            background: rgba(0, 0, 0, 0.1);
                            max-height: 12rem;
                            height: 2rem;
                          "
                          @keydown.enter.prevent="onSubmit"
                        />
                      </div>
                      <div class="col-2 px-0 d-flex align-items-end">
                        <button
                          :disabled="chatText === ''"
                          class="btn btn-danger text-white"
                        >
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
import { OpenAI } from "langchain/llms/openai";
import { BufferMemory } from "langchain/memory";
import { ConversationChain } from "langchain/chains";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { Calculator } from "langchain/tools/calculator";
// import { SerpAPI } from "langchain/tools";
import { initializeAgentExecutorWithOptions } from "langchain/agents";
import Vue from "vue";

export default {
  name: "prompting-view",
  components: {
    MessageView,
  },

  data: () => ({
    chatText: "",
    chatMode: "normal_chat",
    user: {
      name: "You",
      id: 2,
    },
    // init_messages: [
    //   {
    //     author: "AI",
    //     text: "Hey, how can I help you today?",
    //     uid: 1,
    //     isMine: false,
    //   },
    // ],
    messages: [],
    chatModel: null,
    openAIApiKey: "",
    // searchKey: "",
    chatModelList: [],
    selectedModel: "gpt-3.5-turbo",
  }),

  created() {
    this.messages = [];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    // this.searchKey = localStorage.getItem("searchKey");
    if (this.openAIApiKey != null) {
      this.initChatModel(this.chatMode, this.selectedModel);
    }
    this.fetchModels();
  },

  methods: {
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
            if (this.chatMode === "normal_chat") {
              response = res.response;
            } else {
              if (res.intermediateSteps.length > 0) {
                response += "```\n";
                for (let i = 0; i < res.intermediateSteps.length; i++) {
                  const step = res.intermediateSteps[i];
                  console.log(step);
                  response += `Action [${i + 1}] tool:\t ${
                    step.action.tool
                  } \n`;
                  response += `Action [${i + 1}] Input:\t ${
                    step.action.toolInput
                  } \n`;
                  response += `Action [${i + 1}] Output:\t ${
                    step.observation
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
    // saveSearchKey() {
    //   localStorage.setItem("searchKey", this.searchKey);
    //   // TODO: show success message
    // },
    async initChatModel(chatmode, chatmodel) {
      if (chatmode === "normal_chat") {
        this.chatModel = new ConversationChain({
          memory: new BufferMemory(),
          llm: new OpenAI({
            modelName: chatmodel,
            openAIApiKey: this.openAIApiKey,
          }),
        });
      } else if (chatmode === "agent_chat") {
        process.env.LANGCHAIN_HANDLER = "langchain";
        const model = new ChatOpenAI({
          modelName: chatmodel,
          openAIApiKey: this.openAIApiKey,
        });
        // console.log(this.searchKey);
        const tools = [
          new Calculator(),
          // new SerpAPI(this.searchKey, {}, "/serp-api",) // see https://github.com/hwchase17/langchainjs/blob/9523a2e/langchain/src/tools/serpapi.ts#L303
        ];
        this.chatModel = await initializeAgentExecutorWithOptions(
          tools,
          model,
          {
            agentType: "chat-conversational-react-description", // automatically creates and uses BufferMemory with the executor.
            returnIntermediateSteps: true,
          }
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
  },

  watch: {
    /* eslint-disable no-unused-vars */
    async chatMode(newValue, oldValue) {
      // TODO: check if the key is valid
      await this.initChatModel(newValue, this.selectedModel);
      this.resetConv();
    },
    /* eslint-disable no-unused-vars */
    async selectedModel(newValue, oldValue) {
      await this.initChatModel(this.chatMode, newValue);
      this.resetConv();
    },
  },
};
</script>

<style scoped>
.message + .message {
  margin-top: 1rem;
}
.message.right {
  margin-left: auto;
}
button:disabled {
  opacity: 0.5;
}
</style>
