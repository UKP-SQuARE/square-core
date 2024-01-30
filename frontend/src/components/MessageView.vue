<template>
  <div :class="['message', { dark }]" class="px-3">
    <strong class="unselectable">{{ author }}&nbsp;&nbsp;</strong>
    <div v-if="isGenerating && text === '' && !done" class="spinner-border spinner-border-sm" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <br />
    <div class="markdown-content" v-html="markdownToHtml(text)"></div>
  </div>
</template>

<script>
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";

marked.use({
  mangle: false,
  headerIds: false,
  ...markedHighlight({
    langPrefix: "hljs language-",
    highlight(code, lang) {
        console.log(code);
        console.log(lang);
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      return hljs.highlight(code, {language}).value;
    },
  }),
});

export default {
  name: "MessageView",
  props: [
    "text", // Content of the message
    "role", // Role of the message
    "isGenerating", // Whether the message is being generated
    "done" // Whether the message has been generated
  ],

  methods: {
    markdownToHtml(md) {
      return marked.parse(md);
    },
  },

  computed: {
    author() {
      return this.role === "human" ? "You" : "AI";
    },
    dark() {
      return this.role === "human";
    },
  },
};
</script>


<style scoped>
.message {
  background: rgba(0, 102, 145, 0.1);
  border-radius: 10px;
  padding: 0.77rem;
  width: fit-content;
  max-width: 85%;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
.message.dark {
  background: rgba(0, 102, 145, 0.3);
}
</style>

<style>
.hljs {
  display: block;
  padding: 0.5em;
  background: #d2d2d2;
}
</style>

