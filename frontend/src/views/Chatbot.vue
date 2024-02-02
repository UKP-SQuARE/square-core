<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class="row row-cols-2">
            <!-- Chat Bereich -->

            <div class="col">
              <!-- Infobox auf der linken Seite -->
              <div class="bg-light border rounded shadow p-3">
                <!-- Dummy-Text -->
                <h4 class="row m-3 ">{{ languageModel }}</h4>
                <div class="bg-light border rounded shadow p-2 m-1">
                  <h6 class="row m-2 p-1">Collected Points: {{ collectedPoints }}</h6>
                </div>
                <div class="bg-light border rounded shadow p-2 m-1">
                  <h6 class="row m-2 p-1">Tasks:</h6>
                  <div class="row m-1 p-1" v-for="task in tasks" :key="task">{{ task }}</div>
                </div>

              </div>

              <!-- Buttons auf der linken Seite -->
              <div class="row mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <!-- router link to cha with query params runQueryParams -->
                  <router-link :to="{ name: 'chatbot_rating' }" class="btn btn-danger btn-lg text-white">
                    Cancel
                  </router-link>
                </div>
              </div>
              <div class="row mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <div class="btn btn-danger btn-lg text-white" @click="openSubmitPopup">
                    Submit Feedback
                  </div>
                </div>
              </div>
            </div>

            <div class="col">
              <div class="bg-light border rounded shadow p-3 ">
                <div class="container">
                  <!-- Chatbereich -->
                  <div class="row">
                    <div class="col md-1">
                      <div class="card">
                        <div class="card-header">
                          Chat
                        </div>
                        <div class="card-body chat-box" ref="chatBox">
                          <!-- Chat-Nachrichten werden hier dynamisch eingefügt -->
                          <div v-for="question in questions" :key="question.id">
                            <div class="d-flex flex-row justify-content-end mb-4">
                              <div class="p-2 ms-2" style="border-radius: 15px; background-color: rgba(57, 192, 237,.2);">
                                <p class="small mb-0"> {{ question.text }}</p>
                              </div>
                            </div>
                            <div v-if="answers[question.id] !== undefined || answerGenerated"
                              class="d-flex flex-row justify-content-start mb-4">
                              <div class="p-2 me-2 border" style="border-radius: 15px; background-color: #fbfbfb;">
                                <p class="small mb-0"> {{ answers[question.id] }}</p>
                              </div>
                              <button @click="openFeedbackHandler(question)" class="round-blue-button">
                                <div> &#8618;</div>
                              </button>
                            </div>
                            <div v-else>
                              <pulse-loader></pulse-loader>
                            </div>

                            <div v-show="openFeedback" class="modal fade show" style="display: block;"
                              @click.self="openFeedback = false">
                              <div class="modal-dialog modal-dialog-centered">
                                <div class="modal-content">
                                  <div class="modal-header">
                                    <h5 class="modal-title">Answer Feedback</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"
                                      @click="openFeedback = false"></button>
                                  </div>
                                  <div class="starplot-container">
                                    <div v-for="metric in metricIds" :key="metric" class="starplot-item">
                                      <div class="row m-1">
                                        <div class="col">
                                          <label :for="currentValues[metric]">{{ metrics[metric] }}</label>
                                        </div>
                                        <div class="col">
                                          <input type="range" class="form-control-range" :id="currentValues[metric]"
                                            v-model="currentValues[metric]" min="1" max="5" />
                                          <span>{{ currentValues[metric] }}</span>


                                        </div>

                                      </div>
                                    </div>
                                    <div class="d-grid gap-1 d-md-flex justify-content-md-center m-2">
                                      <div class="btn btn-danger btn-lg text-white" @click="submitAnswerFeedback()">
                                        Submit
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Eingabebereich -->
                  <div class="row align-items-end">
                    <div class="col">
                      <div class="input-group">
                        <input v-model="newQuestion" @keyup.enter="sendQuestion" type="text" class="form-control"
                          placeholder="Write a message" />
                        <div class="input-group-append">
                          <button @click="sendQuestion" class="btn btn-primary">Send</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="openPopup" class="modal fade show" style="display: block;" @click.self="openPopup = false">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Feedback</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"
              @click="openPopup = false"></button>
          </div>
          <div class="modal-body">
            <h6 class="row m-2 p-1">Collected Points: {{ collectedPoints + 200 }}</h6>

            <div id="chart">
              <apexchart type="radar" height="350" :options="chartOptions" :series="results"></apexchart>
            </div>
            <div class="row">
              <div class="col mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <div class="btn btn-danger btn-lg text-white" @click="openPopup = false">
                    Cancel
                  </div>
                </div>
              </div>
              <div class="col mt-4">
                <div v-if="questions.length !== 0" class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <div @click="submitFeedback()">
                    <router-link :to="{ name: 'chatbot_rating' }" class="btn btn-danger btn-lg text-white">
                      Submit
                    </router-link>
                  </div>
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
/* eslint-disable */
import Vue from 'vue'
import Query from '@/components/Query.vue'
import Results from '@/components/Results.vue'
import VueApexCharts from 'vue-apexcharts'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'
import axios from 'axios'
export default Vue.component('run-qa', {
  data() {


    return {
      languageModel: "Phi language model",
      tasks: ["Ask something about the weather today.", "Ask general things!", "Ask personal things about the language model"],
      collectedPoints: 100,
      answerGenerated: false,
      metricIds: [0, 1, 2, 3, 4, 5],
      metrics: ['Factual correctness', 'Language generation', 'Context', 'Coverage', 'Clarity of response', 'Harmfulness'],
      newQuestion: '',
      questions: [],
      answers: [],
      openPopup: false,
      openFeedback: false,
      currentValues: [],
      defaultValues: ['3', '3', '3', '3', '3', '3'],
      answerValues: [],
      results: [],
      currentQuestionId: 0,
      chartOptions: {
        chart: {
          height: 350,
          type: 'radar',
        },
        title: {
          text: 'Feedback'
        },
        xaxis: {
          categories: ['Factual correctness', 'Language generation', 'Context', 'Coverage', 'Clarity of response', 'Harmfulness']
        }
      },

    };
  },
  components: {
    Query,
    Results,
    apexchart: VueApexCharts,
    PulseLoader,

  },
  methods: {
    async sendQuestion() {
      var questionText = this.newQuestion.trim();
      if (questionText !== '') {
        var questionId = this.questions.length
        this.questions.push({
          id: questionId,
          text: questionText,
        });
        this.newQuestion = '';
        this.answerGenerated = false
        await this.generateAnswer(questionId)
        this.answerGenerated = true

        this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight;


      }
    },
    async generateAnswer(questionId) {
      try {
        if (false) { }
        var questionText = this.questions[questionId]
        var postData = { "model": "phi", "messages": [{ "role": "user", "content": questionText["text"] }], "stream": false }

        const response = await axios.post('http://194.163.130.51:11434/api/chat', postData)
        var answer = ""
        var jsonData = response.data
        var contents = ""
        try {
          contents = jsonData["message"]["content"];
        } catch (error) {
          console.error(`Parse error ${line}`);
          return null;
        }
        answer = contents;
        this.answers[questionId] = answer
      } catch (error) {
        this.answers[questionId] = "Connection Error"
        console.error('Connection error', error);
      }


    },
    openFeedbackHandler(question) {
      var id = question.id;
      this.currentQuestionId = id;
      if (this.answerValues[id] !== undefined) {
        this.currentValues = this.answerValues[id];
      }
      else {
        this.currentValues = [...this.defaultValues];
      }
      this.openFeedback = true;

    },
    submitAnswerFeedback() {
      var id = this.currentQuestionId;
      if (this.answerValues[id] === undefined) {
        this.answerValues[id] = this.currentValues;
        this.collectedPoints += 50;
      }
      else {
        this.answerValues[id] = this.currentValues;
      }
      this.currentValues = [...this.defaultValues];
      this.openFeedback = false;
    },
    openSubmitPopup() {
      if (this.answerValues.length == 0) {
        this.results[0] = {
          name: "Default Data",
          data: [...this.defaultValues]
        };


      }
      else {
        var keys = Object.keys(this.answerValues);
        var averageValues = this.defaultValues.map(() => 0);

        for (let i = 0; i < keys.length; i++) {
          var currentValues = this.answerValues[keys[i]];
          for (let j = 0; j < currentValues.length; j++) {
            averageValues[j] += parseInt(currentValues[j]);
          }
        }

        for (let k = 0; k < averageValues.length; k++) {
          averageValues[k] = averageValues[k] / keys.length;
        }
        this.results[0] = {
          name: "Calculated Feedback",
          data: averageValues
        }

      }
      this.openPopup = true;
    },
    submitFeedback() {

    },
    cancel() {
      // Logik für den "Cancel"-Button
      console.log('Cancel button clicked');
    },
    submitFeedback() {
      // Logik für den "Submit Feedback"-Button
      this.collectedPoints += 200;
      console.log('Submit Feedback button clicked');
    },
  }
})

</script>

<style scoped>
/* Stile für das Layout */
#app {
  display: flex;
  height: 80vh;
  flex-direction: row;
  justify-content: space-between;
}

#infobox {
  flex: 1;
  display: flex;
  flex-direction: column;

}


.question {
  text-align: right;

}

.answer {
  text-align: left;
}



.chat-box {
  height: 400px;
  overflow-y: auto;
}

.round-blue-button {
  display: inline-block;
  padding: 5px 10px;
  font-size: 16px;
  height: 50px;
  width: 50px;
  font-weight: bold;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  border: none;
  border-radius: 50%;
  color: #fff;
  background-color: #3498db;
  /* Blaue Farbe, du kannst dies nach Bedarf ändern */
  transition: background-color 0.3s ease;
}
</style>