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
                <div>
                  <form @submit.prevent="onSubmit">
                    <div class="row">
                      <div class="col-2 px-0 d-flex align-items-end justify-content-end">
                        <button :disabled="messages.length === 1" type="button" @click="resetConv"
                          class="btn btn-primary border rounded-5"> Reset </button>
                      </div>
                      <div class="col-8">
                        <textarea v-model="chatText" placeholder="Write a message" 
                        type="text" class="form-control border-0 p-2 m-0"
                        style="background: rgba(0, 0, 0, 0.1); max-height: 12rem; height: 2rem;"/>
                      </div>
                      <div class="col-2 px-0 d-flex align-items-end">
                        <button :disabled="chatText === ''" class="btn btn-primary">Send</button>
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
