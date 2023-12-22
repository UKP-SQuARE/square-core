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
                  <div class="btn btn-danger btn-lg text-white" @click="openPopup = true">
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
                              <button type="button" class="btn btn-success" @click="openFeedback = true">Feedback</button>
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
                                    <div v-for="metric in metrics" :key="metric" class="starplot-item">
                                      <div class="row m-1">
                                        <div class="col">
                                          <label :for="'element_' + metric">{{ metric }}</label>
                                        </div>
                                        <div class="col">
                                          <input type="range" class="form-control-range" :id="'element_' + metric"
                                            v-model="values[metric]" min="1" max="5" />
                                          <span>{{ values[metric] }}</span>
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
              <apexchart type="radar" height="350" :options="chartOptions" :series="series"></apexchart>
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

export default Vue.component('run-qa', {
  data() {


    return {
      metrics: ['Factual correctness', 'Language generation', 'Context', 'Coverage', 'Clarity of response', 'Harmfulness'],
      newQuestion: '',
      questions: [],
      answers: [],
      openPopup: false,
      openFeedback: false,
      values: [1, 1, 1, 1, 1],
      series: [{
        name: 'Your Feedback',
        data: [1, 2, 3, 4, 5, 4],
      },
      {
        name: 'Others Feedback',
        data: [2, 3, 4, 5, 4, 5],
      }
      ],
      chartOptions: {
        chart: {
          height: 350,
          type: 'radar',
        },
        title: {
          text: 'Feeback'
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
    sendQuestion() {
      if (this.newQuestion.trim() !== '') {
        this.questions.push({
          id: this.questions.length + 1,
          sender: 'Q', // Du kannst hier den Benutzernamen ändern
          text: this.newQuestion.trim(),
          answer: this.generateAnswer(this.newQuestion.trim())
        });

        // Scrollen zum Ende des Chats nach dem Senden einer Nachricht
        this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight;

        // Zurücksetzen des Eingabefelds
        this.newQuestion = '';
      }
    },
    generateAnswer() {
      this.answers.push({
        id: this.answers.length + 1,
        sender: 'A', // Du kannst hier den Benutzernamen ändern
        text: "dummy",
      });
      return ({
        id: this.answers.length + 1,
        sender: 'A', // Du kannst hier den Benutzernamen ändern
        text: "dummy",
      })
    }
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
</style>