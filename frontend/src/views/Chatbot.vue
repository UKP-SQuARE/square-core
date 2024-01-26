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
                <h4>Sprachmodell</h4>
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
                    <div class="col-md-8 offset-md-2">
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
                            <div class="d-flex flex-row justify-content-start mb-4">
                              <div class="p-2 me-2 border" style="border-radius: 15px; background-color: #fbfbfb;">
                                <p class="small mb-0"> {{ question.answer.text }}</p>
                              </div>
                              <button @click="openFeedbackHandler(question.text)" class="round-blue-button">

                                <div> &#8618;</div>
                              </button>
                            </div>

                            <div v-if="openFeedback" class="modal fade show" style="display: block;"
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
                                          <label :for="'element_' + metric">{{ metrics[metric] }}</label>
                                        </div>
                                        <div class="col">
                                          <input type="range" class="form-control-range" :id="'element_' + metric"
                                            v-model="currentValues[metric]" min="1" max="5" />
                                          <span>{{ currentValues[metric] }}</span>
                                        </div>

                                      </div>
                                    </div>
                                    <div class="d-grid gap-1 d-md-flex justify-content-md-center m-2">
                                      <div class="btn btn-danger btn-lg text-white"
                                        @click="submitAnswerFeedback(question.text)">
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
                          placeholder="Schreibe eine Nachricht..." />
                        <div class="input-group-append">
                          <button @click="sendQuestion" class="btn btn-primary">Senden</button>
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
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
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
import RadarChart from '../components/RadarChart.vue'
import axios from 'axios'
export default Vue.component('run-qa', {
  data() {


    return {
      metricIds: [0, 1, 2, 3, 4, 5],
      metrics: ['Factual correctness', 'Language generation', 'Context', 'Coverage', 'Clarity of response', 'Harmfulness'],
      newQuestion: '',
      questions: [],
      answers: [],
      openPopup: false,
      openFeedback: false,
      currentValues: [],
      defaultValues: ['3', '3', '3', '3', '3', '3'],
      answerValues: {},
      results: [
      ],
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

  },
  methods: {
    async sendQuestion() {
      if (this.newQuestion.trim() !== '') {
        this.questions.push({
          id: this.questions.length + 1,
          sender: 'Q', // Du kannst hier den Benutzernamen ändern
          text: this.newQuestion.trim(),
          answer: await this.generateAnswer(this.newQuestion.trim())
        });

        // Scrollen zum Ende des Chats nach dem Senden einer Nachricht
        this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight;

        // Zurücksetzen des Eingabefelds
        this.newQuestion = '';
      }
    },
    async generateAnswer(question) {
      try {
        var postData = { "model": "phi", "messages": [{ "role": "user", "content": question }], "stream": true }
        const response = await axios.post('http://194.163.130.51:11434/api/chat', postData);
        var answer = ""
        var jsonData = response.data
        const jsonLines = jsonData.split('\n');

        const contents = jsonLines.map(line => {
          try {
            const json = JSON.parse(line);
            return json.message.content;
          } catch (error) {
            console.error(`Fehler beim Parsen der Zeile: ${line}`);
            return null;
          }
        });
        answer=contents.join(" ");
        this.answers.push({
          id: this.answers.length + 1,
          sender: 'A', 
          text: answer,
        });
      } catch (error) {
        console.error('Connection error', error);
      }


      return ({
        id: this.answers.length + 1,
        sender: 'A', 
        text: answer,
      })
    },
    openFeedbackHandler(text) {
      if (text in this.answerValues) {
        this.currentValues = this.answerValues[text];
      }
      else {
        this.currentValues = this.defaultValues;
      }
      this.openFeedback = true;

    },
    submitAnswerFeedback(text) {
      this.answerValues[text] = this.currentValues;
      this.currentValues = [];
      this.openFeedback = false;

    },
    openSubmitPopup() {
      if (this.answerValues.length == 0) {
        this.results[0] = {
          name: "Default Data",
          data: this.defaultValues
        };


      }
      else {
        var keys = Object.keys(this.answerValues)
        var averageValues = this.answerValues[keys[0]].map(i => parseInt(i));

        for (let k = 0; k < averageValues.length; k++) {
          for (let i = 1; i < keys.length; i++) {
            averageValues[k] = parseInt(this.answerValues[keys[i]]) + averageValues[k];
          }
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