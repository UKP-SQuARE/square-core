<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row">
            <div class="col col-3 d-none d-md-block">
              <form class="form-inline" @submit.prevent="saveKey">
                <div class="form-group">
                  <div class="row">
                    <div class="col-8 px-0">
                      <input
                        type="password"
                        class="form-control py-1 mx-0"
                        id="open-ai-key"
                        placeholder="OpenAI key (locally stored)"
                        title="Your key is stored locally and not shared with anyone"
                        v-model="openAIApiKey"
                      />
                    </div>
                    <div class="col-4 px-2">
                      <button
                        type="submit"
                        class="btn btn-primary mx-0 px-4 py-1"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </div>
            <div
              class="col col-md-9 border rounded p-3 bg-white"
              style="height: 70vh"
            >
              <div class="app">
                <div ref="messages" class="messages">
                  <MessageView
                    v-for="message in messages"
                    :key="message.id"
                    :class="['message', { right: message.isMine }]"
                    :dark="message.isMine"
                    :text="message.text"
                    :author="message.author"
                  />
                </div>
                <div class="chat-box">
                  <form class="chat-box" @submit.prevent="onSubmit">
                    <button
                      :disabled="messages.length === 1"
                      type="button"
                      @click="resetConv"
                    >
                      Reset
                    </button>
                    <!-- <input v-model="chatText" placeholder="Write a message" type="text"/> -->
                    <textarea
                      v-model="chatText"
                      placeholder="Write a message"
                      type="text"
                    />
                    <button :disabled="chatText === ''">Send</button>
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
import Vue from "vue";

export default {
  name: "prompting-view",
  components: {
    MessageView,
  },

  data: () => ({
    chatText: "",
    user: {
      name: "John",
      id: 2,
    },
    init_messages: [
      {
        author: "AI",
        text: "Hey, how can I help you today?",
        uid: 1,
        isMine: false,
      },
    ],
    messages: [],
    chatChain: null,
    openAIApiKey: "",
  }),

  created() {
    this.messages = [...this.init_messages];
    this.openAIApiKey = localStorage.getItem("openAIApiKey");
    if (this.openAIApiKey != null) {
      this.chatChain = new ConversationChain({
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
            // show worning message about the key
          }else{
            const res = await this.chatChain.call({ input: text });
            this.messages.push({
              author: "AI",
              text: res.response,
              uid: 1,
              isMine: false,
            });

            Vue.nextTick(() => {
              this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
            });
          }
        } catch (err) {
          if(err.response.data.error.code === "invalid_api_key"){
            // show error message about the key  
          }else{
            // show general error message
          }
        }
      }
    },
    resetConv() {
      console.log("reset");
      this.chatText = "";
      this.messages.splice(1, this.messages.length);
      this.chatChain.memory.clear();
    },
    saveKey() {
      localStorage.setItem("openAIApiKey", this.openAIApiKey);
      // show success message
    },
  },
};
</script>

<style scoped>
button {
  border: 0;
  background: #2a60ff;
  color: white;
  cursor: pointer;
  padding: 1rem;
}

textarea {
  border: 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.1);
  width: min(100%, 30rem);
  flex-grow: 1;
  font-size: 1.2rem;
}

.app {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.messages {
  flex-grow: 1;
  overflow: auto;
  padding: 1rem;
}

.message + .message {
  margin-top: 1rem;
}

.message.right {
  margin-left: auto;
}
.chat-box {
  width: 100%;
  display: flex;
}

button:disabled {
  opacity: 0.5;
}
</style>
