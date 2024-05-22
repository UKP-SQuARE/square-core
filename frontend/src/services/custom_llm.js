/* eslint-disable no-unused-vars */
import { BaseChatModel } from 'langchain/chat_models/base';
import { BaseLLM } from 'langchain/llms/base';

import { 
  generateText,
  generateChatStreamReplicate,
  generateCompletionStreamReplicate,
} from '@/api'
import { 
  AIMessage,
} from 'langchain/schema';


export class CustomChatModel extends BaseChatModel {
  model_identifier = "";
  temperature = 0.7;
  top_p = 0.9;
  max_new_tokens = 1000;
  streaming = false;

  constructor(params) {
    super(params);
    this.model_identifier = params.model_identifier;
    this.temperature = params.temperature;
    this.top_p = params.top_p;
    this.max_new_tokens = params.max_new_tokens;
    this.streaming = params.streaming;
  }

  async _llmType() {
    return 'custom_chat_model'
  }

  _parseChatHistory(history){
    const chatHistory = [];
    let systemMessage = "";
  
    for (const message of history) {
      if ("content" in message) {
        if (message._getType() === "human") {
          chatHistory.push({ role: "human", text: message.content });
        } else if (message._getType() === "ai") {
          chatHistory.push({ role: "ai", text: message.content });
        } else if (message._getType() === "system") {
          systemMessage = message.content;
        }
      }
    }
    return [chatHistory, systemMessage];
  }

  async _generate(
    messages, 
    options,
    runManager
  ) {
    const [messageHistory, systemMessage] = this._parseChatHistory(messages);
    const bodyData = {
      model_identifier: this.model_identifier,
      messages: messageHistory,
      system_message: systemMessage,
      temperature: this.temperature,
      top_p: this.top_p,
      max_new_tokens: this.max_new_tokens,
      echo: false, // false will make model return only last message
      generation_mode: "chat"
    }
    if (this.streaming === false) {
      const response = await generateText(bodyData, this.streaming)
      const generations = [
        {text: response.data.text, message: new AIMessage(response.data.text)}
      ]
      return {
        generations: generations,
        llmOutput: { tokenUsage: response.data.usage }
      }
    } else {
      let readableStream = await generateText(bodyData, this.streaming);
      readableStream = readableStream.body;
      const decoder = new TextDecoder();
      const reader = readableStream.getReader();
      let buffer = '';
      let receivedText = '';
      let lastLength = 0;
      let done, value; 

      while (!done){
        ({done, value} = await reader.read()); 
        
        const messageChunk =  decoder.decode(value, { stream: true });
        buffer += messageChunk;

        // sometimes the buffer contains several messages so we split them
        const parts = buffer.split('\u0000');
        for (let i = 0; i < parts.length - 1; i++) {
          try {
            const jsonChunk = JSON.parse(parts[i]);
            const newText = jsonChunk.text.substring(lastLength);
            lastLength = jsonChunk.text.length;
            receivedText += newText;
            runManager.handleLLMNewToken(newText, jsonChunk.usage)
          } catch (error) {
            console.error(error);
          }
        }
        // Keep the last incomplete part in the buffer
        buffer = parts[parts.length - 1];

        if (options.signal.aborted){
          throw new Error("AbortError");
        }

      }
      const generations = [
        {text: receivedText, message: new AIMessage(receivedText)}
      ]
      return {
        generations: generations,
        llmOutput: { tokenUsage: 0 }
      }
    }
  }
}


export class ReplicateChatModel extends BaseChatModel {
  model_identifier = "";
  temperature = 0.7;
  top_p = 0.9;
  max_new_tokens = 1000;
  streaming = true;
  replicateKey = "";

  constructor(params) {
    super(params);
    this.model_identifier = params.model_identifier;
    this.temperature = params.temperature;
    this.top_p = params.top_p;
    this.max_new_tokens = params.max_new_tokens;
    this.streaming = params.streaming;
    this.replicateKey = params.replicateKey;
  }

  async _llmType() {
    return 'replicate_model'
  }

  _parseChatHistory(history){
    const chatHistory = [];
    for (const message of history) {
      if ("content" in message) {
        if (message._getType() === "human") {
          chatHistory.push({ role: "human", text: message.content });
        } else if (message._getType() === "ai") {
          chatHistory.push({ role: "ai", text: message.content });
        } else if (message._getType() === "system" && message.content !== "") {
          chatHistory.push({ role: "system", text: message.content });
        }
      }
    }
    return chatHistory;
  }
  
  async _generate(
    messages,
    options,
    runManager
  ) {
    const messageHistory = this._parseChatHistory(messages);
    const bodyData = {
      model_identifier: this.model_identifier,
      messages: messageHistory,
      temperature: this.temperature,
      top_p: this.top_p,
      max_new_tokens: this.max_new_tokens,
    }

    const response = await generateChatStreamReplicate(bodyData, this.replicateKey);
    const streamUrl = response.data.url

    let receivedText = '';

    const waitForDoneEvent = new Promise((resolve, reject) => {
      const source = new EventSource(streamUrl);
    
      const onOutput = (event) => {
        if (options.signal?.aborted) {
          source.removeEventListener("output", onOutput);
          source.removeEventListener("done", onDone);
          source.close();
          reject(new Error("AbortError"));
          return;
        }
    
        const next_token = event.data;
        if (this.streaming){
          runManager?.handleLLMNewToken(next_token);
        }
        receivedText += next_token;
      };
    
      const onDone = (_) => {
        source.removeEventListener("output", onOutput);
        source.removeEventListener("done", onDone);
        source.close();
        resolve();
      };
    
      source.addEventListener("output", onOutput);
      source.addEventListener("done", onDone);
    });
    
    await waitForDoneEvent;

    const generations = [
      {text: receivedText, message: new AIMessage(receivedText)}
    ]
    return {
      generations: generations,
      llmOutput: { tokenUsage: 0 }
    }
  }
}


export class ReplicateGenerativeModel extends BaseLLM {
  model_identifier = "";
  top_p = 0.9;
  temperature = 0.7;
  max_new_tokens = 1000;
  streaming = false;
  replicateKey = "";

  constructor(params) {
    super(params);
    this.model_identifier = params.model_identifier;
    this.top_p = params.top_p;
    this.temperature = params.temperature;
    this.max_new_tokens = params.max_new_tokens;
    this.streaming = params.streaming;
    this.replicateKey = params.replicateKey;
  }

  async _llmType() {
    return 'replicate_generative_model'
  }

  async _generate(prompts) {
    const bodyData = {
      model_identifier: this.model_identifier,
      top_p: this.top_p,
      temperature: this.temperature,
      max_new_tokens: this.max_new_tokens,
      prompt: prompts[0],
    }
    const response = await generateCompletionStreamReplicate(bodyData, this.replicateKey);
    const streamUrl = response.data.url

    let receivedText = '';

    const waitForDoneEvent = new Promise((resolve, _) => {
      const source = new EventSource(streamUrl);
      source.addEventListener("output", (event) => {
        const next_token = event.data;
        receivedText += next_token;
      })
      source.addEventListener("done", (_) => {
        source.close();
        resolve();
      });
    });

    await waitForDoneEvent;

    const generations = [[
      {
        text: receivedText.trim(), 
        generationInfo: {}
      }
    ]]
    return {
      generations: generations,
      llmOutput: { tokenUsage: 0 }
    }
  }
}


export class CustomGenerativeModel extends BaseLLM {
  model_identifier = "";
  temperature = 0.7;
  top_p = 0.9;
  max_new_tokens = 1000;
  streaming = false;

  constructor(params) {
    super(params);
    this.model_identifier = params.model_identifier;
    this.temperature = params.temperature;
    this.top_p = params.top_p;
    this.max_new_tokens = params.max_new_tokens;
    this.streaming = params.streaming;
  }

  async _llmType() {
    return 'custom_generative_model'
  }

  async _generate(prompts) {
    const bodyData = {
      model_identifier: this.model_identifier,
      prompt: prompts[0],
      system_message: "",
      temperature: this.temperature,
      top_p: this.top_p,
      max_new_tokens: this.max_new_tokens,
      echo: false, // false will make model return only last message
      generation_mode: "completion"
    }
    const response = await generateText(bodyData, this.streaming)
    const generations = [[
      {
        text: response.data.text.trim(),
        generationInfo: {}
      }
    ]]
    return {
      generations: generations,
      llmOutput: { tokenUsage: response.data.usage }
    }
  }
}
