<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div class="bg-light border rounded shadow p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container-fluid">
          <div class=""></div>
          <!-- Infobox auf der linken Seite -->
          <div class="bg-light border rounded shadow p-3">
            <!-- Dummy-Text -->
            <h4>Sprachmodell</h4>
            <div class="container">
              <div class="row">
                <!-- Chatbereich -->
                <div class="col">
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
                            <button @click="openFeedback = true" class="round-blue-button">
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
                                        <span>{{ answerValues[question.text][metric] }}</span>
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

                <div class="col">
                  <div id="chart">
                    <apexchart type="radar" height="350" :options="chartOptions" :series="series"></apexchart>
                  </div>
                </div>
              </div>
            </div>
            <div class="row">
              <!-- Buttons auf der linken Seite -->
              <div class="col mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <div class="btn btn-danger btn-lg text-white" @click="handleDisprove">
                    Disprove
                  </div>
                </div>
              </div>
              <div class="col mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <!-- router link to cha with query params runQueryParams -->
                  <router-link :to="{ name: 'chatbot_rating' }" class="btn btn-danger btn-lg text-white">
                    Cancel
                  </router-link>
                </div>
              </div>
              <div class="col mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <div class="btn btn-danger btn-lg text-white" @click="handleValidate">
                    Validate
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
              <h5 class="modal-title">Feedback Validation</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"
                @click="openPopup = false"></button>
            </div>
            <div class="modal-body">
              <div class="d-flex justify-content-center align-items-center">
                <textarea v-model="optionalText" placeholder="Optional message" cols="50" rows="8"></textarea>
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
      validate:true,
      metricIds: [0, 1, 2, 3, 4, 5],
      metrics: ['Factual correctness', 'Language generation', 'Context', 'Coverage', 'Clarity of response', 'Harmfulness'],
      newQuestion: '',
      optionalText: '',
      questions: [{
        id: 0,
        text: "Dummy?",
        answer: {
          text: "dummy"
        },
      },
      {
        id: 1,
        text: "Dummy?",
        answer: {
          text: "dummy"
        },
      },
      {
        id: 2,
        text: "Dummy?",
        answer: {
          text: "dummy"
        },
      },
      {
        id: 3,
        text: "Dummy?",
        answer: {
          text: "dummy"
        },
      }
      ],
      answerValues: {
        'Dummy?': ['3', '3', '3', '3', '3', '3']
      },
      openPopup: false,
      openFeedback: false,
      series: [{
        name: 'Your Feedback',
        data: [1, 2, 3, 4, 5, 4],
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

    handleDisprove(){
      this.validate=false;
      this.openPopup=true;
    },
    handleValidate(){
      this.validate=true;
      this.openPopup=true;
    },

    cancel() {
      // Logik für den "Cancel"-Button
      console.log('Cancel button clicked');
    },
    submitFeedback() {
      // Logik für den "Submit Feedback"-Button
      console.log(validate);
    },
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

.round-blue-button {
  display: inline-block;
  padding: 5px 10px;
  font-size: 16px;
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