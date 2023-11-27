import { BaseChatModel } from 'langchain/chat_models/base';
import { BaseLLM } from 'langchain/llms/base';

import { 
  generateText,
  // generateTextStream
} from '@/api'
import { 
  AIMessage,
  // AIMessageChunk
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
    }

    console.log("bodyData of custom chat model")
    console.log(bodyData)

    try {
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
        }
        const generations = [
          {text: receivedText, message: new AIMessage(receivedText)}
        ]
        return {
          generations: generations,
          llmOutput: { tokenUsage: 0 }
        }
      }
    } catch (error) {
      console.log(error)
      return { error: error }
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

  _parsePrompt(prompt){
    const promptMessage = { role: "human", text: prompt }; // doing this to work with chat models we deploy
    return [promptMessage];
  }

  async _generate(prompts) {
    const promptMessage = this._parsePrompt(prompts[0]);
    const bodyData = {
      model_identifier: this.model_identifier,
      messages: promptMessage,
      system_message: "Answer only with 1 or 0.",
      temperature: this.temperature,
      top_p: this.top_p,
      max_new_tokens: this.max_new_tokens,
      echo: false, // false will make model return only last message
    }
    try {
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
    } catch (error) {
      console.log(error)
      return { error: error }
    }
  }
}
