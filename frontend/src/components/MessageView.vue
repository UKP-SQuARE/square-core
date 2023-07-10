<template>
  <div :class="['message', { dark }]">
    <strong>{{ author }}</strong>
    <br />
    <div v-html="markdownToHtml(text)"></div>
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
    "author", // Author of the message
    "dark", // Background variant of the box
  ],
  methods: {
    markdownToHtml(md) {
      return marked.parse(md);
    },
  },
};
</script>



<style scoped>
.message {
  background: #ebebeb;
  border-radius: 10px;
  padding: 0.77rem;
  width: fit-content;
}
.message.dark {
  background: #5fc9f8;
}
</style>

<style>
.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #d2d2d2;
}
</style>

