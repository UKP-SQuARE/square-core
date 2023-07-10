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
                      <label for="open-ai-key" >OpenAI key (locally stored)</label>
                      <input
                        type="password"
                        class="form-control"
                        id="open-ai-key"
                        placeholder="OpenAI key (locally stored)"
                        title="Your key is stored locally and not shared with anyone"
                        v-model="openAIApiKey"
                      />
                    </div>
                    <div class="col-3 ps-0 d-flex align-items-end">
                      <button
                        type="submit"
                        class="btn btn-primary px-3"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </div>
                <div class="form-group">
                  <label for="exampleFormControlSelect1">Chat Mode</label>
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
              <div style="height: 100%; flex-direction: column; display: flex;">
                <div ref="messages" class="messages" style="  flex-grow: 1; overflow: auto; padding: 1rem;">
                  <MessageView
                    v-for="message in messages"
                    :key="message.id"
                    :class="['message', { right: message.isMine }]"
                    :dark="message.isMine"
                    :text="message.text"
                    :author="message.author"
                  />
                </div>
                <div class="mt-3">
                  <form @submit.prevent="onSubmit">
                    <div class="row">
                      <div class="col-2 px-0 d-flex align-items-end justify-content-end">
                        <button :disabled="messages.length === 1" type="button" @click="resetConv"
                          class="btn btn-primary border rounded-5"> Reset </button>
                      </div>
                      <div class="col-8">
                        <textarea v-model="chatText" placeholder="Write a message" 
                        type="text" class="form-control border-0 p-2 m-0 auto-resize"
                        style="background: rgba(0, 0, 0, 0.1); max-height: 12rem; height: 2rem;"
                        @keydown.enter.prevent="onSubmit"/>
                      </div>
                      <div class="col-2 px-0 d-flex align-items-end">
                        <button :disabled="chatText === ''" class="btn btn-danger text-white">Send</button>
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
    init_messages: [
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      }
    ],
    messages: [],
    chatModel: null,
    openAIApiKey: "",
  }),

  created() {
    this.messages = [...this.init_messages];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    if (this.openAIApiKey != null) {
      this.chatModel = new ConversationChain({
        memory: new BufferMemory(),
        llm: new OpenAI({
          modelName: "gpt-3.5-turbo",
          openAIApiKey: this.openAIApiKey,
        }),
      });
    }
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
          if(this.openAIApiKey === ""){
            // TODO: show worning message about the key
          }else{
            const res = await this.chatModel.call({ input: text });
            console.log(res)

            let response = ""; 

            if (this.chatMode === "normal_chat"){
              response = res.response;
            }else{
              // for loop with index for the intermediate steps
              for (let i = 0; i < res.intermediateSteps.length; i++) {
                const step = res.intermediateSteps[i];
                response += "Action" + (i + 1) + ": ";
                response += step.action.log + "\n";
              }
              response += "Final Answer: " + res.output;
            }
            console.log(response)


            this.messages.push({
              author: "AI",
              text: response,
              uid: 1,
              isMine: false,
            });

            Vue.nextTick(() => {
              this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
            });

            console.log(this.chatModel)
          }
        } catch (err) {
          console.log(err.message)
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
      this.messages.splice(1, this.messages.length);
      // this.chatModel.memory.clear();
    },
    saveKey() {
      localStorage.setItem("openAIApiKey", this.openAIApiKey);
      // show success message
    }
  },

  watch: {
    async chatMode(newValue, oldValue) {
      if (newValue === "normal_chat") {
        this.chatModel = new ConversationChain({
          memory: new BufferMemory(),
          llm: new OpenAI({
            modelName: "gpt-3.5-turbo",
            openAIApiKey: this.openAIApiKey,
          }),
        });
        console.log("normal chat ready");
      } else if (newValue === "agent_chat") {
        process.env.LANGCHAIN_HANDLER = "langchain";
        const model = new ChatOpenAI({
          modelName: "gpt-3.5-turbo",
          openAIApiKey: this.openAIApiKey,
        });
        const tools = [
          new Calculator()
        ]
        this.chatModel = await initializeAgentExecutorWithOptions(tools, model, {
          agentType: "chat-conversational-react-description", // automatically creates and uses BufferMemory with the executor.
          returnIntermediateSteps: true,
        }); 
        console.log("agent ready");
      }

      this.resetConv();

      console.log(newValue, oldValue);
    }
  }

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
