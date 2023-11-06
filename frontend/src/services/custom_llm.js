import { BaseChatModel } from 'langchain/chat_models/base'
import { 
  generateText,
  // generateTextStream
} from '@/api'
import { 
  AIMessage,
  // AIMessageChunk
} from 'langchain/dist/schema';

export default class CustomChatModel extends BaseChatModel {
  model_identifier = "";
  temperature = 0.7;
  top_p = 0.9;
  max_new_tokens = 1000;

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


  async _generate(messages) {
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
      } 

      // TODO: see openai file of the langchainjs repo for the streaming implementation
      // else {
      //   const stream = generateTextStream(bodyData);
      //   const finalChunks = {};

      //   for await (const chunk of stream) {
      //     const index =
      //       (chunk.generationInfo as NewTokenIndices)?.completion ?? 0;
      //     if (finalChunks[index] === undefined) {
      //       finalChunks[index] = chunk;
      //     } else {
      //       finalChunks[index] = finalChunks[index].concat(chunk);
      //     }
      //   }
      // }


    } catch (error) {
      console.log(error)
      return { error: error }
    }
  }
}
