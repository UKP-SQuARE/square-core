<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
        </div>
        <div class="modal-body">
          <div class="container text-center">
            <div class="row">
              <div class="col-12">
                  <h1>Saliency Map 
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-map" viewBox="0 0 16 16">
                      <path fill-rule="evenodd" d="M15.817.113A.5.5 0 0 1 16 .5v14a.5.5 0 0 1-.402.49l-5 1a.502.502 0 0 1-.196 0L5.5 15.01l-4.902.98A.5.5 0 0 1 0 15.5v-14a.5.5 0 0 1 .402-.49l5-1a.5.5 0 0 1 .196 0L10.5.99l4.902-.98a.5.5 0 0 1 .415.103zM10 1.91l-4-.8v12.98l4 .8V1.91zm1 12.98 4-.8V1.11l-4 .8v12.98zm-6-.8V1.11l-4 .8v12.98l4-.8z"/>
                    </svg>
                    </h1>
                  <hr/>
              </div>
            </div>

            <div class="row">
              <div class="col-2 text-start">
                  <h4>Method:</h4>
              </div>
              <div class="col-2">
                <button v-on:click="postReq('Attention')" type="button" class="btn btn-outline-primary">Attention</button>
              </div>
              <div class="col-2">
                <button @click="postReq('Scaled Attention')" type="button" class="btn btn-outline-primary">Scaled Attention</button>
              </div>
              <div class="col-2">
                <button v-on:click="postReq('Simple Grad')" type="button" class="btn btn-outline-primary">Simple Grad</button>
              </div>
              <div class="col-2">
                <button v-on:click="postReq('Smooth Grad')"  type="button" class="btn btn-outline-primary">Smooth Grad</button>
              </div>
              <div class="col-2">
                <button v-on:click="postReq('Integrated Grad')"  type="button" class="btn btn-outline-primary">Integrated Grad</button>
              </div>
            </div>

            <div v-if="num_show != undefined" class="slidecontainer">
              <div class="row mt-3">
                <div class="col-6 text-start">
                  <h4>Showing the top {{num_show}} most important words</h4>
                </div>
                <div class="col-6">
                  <input type="range" min="1" :max="num_Maxshow" value="this.value" class="form-range" id="Range" oninput="this.nextElementSibling.value = this.value" @click="changeShowNum()"  >
                  <output ></output>
                </div>
              </div>
            </div>
            
            <div class="row mt-3" v-for="(skillResult, index) in currentResults" :key="index">
              <div class="col-12">
                <h4>{{ skillResult.skill.name }}</h4>
                <hr/>
              </div>

              <div v-if="num_show != undefined ">
                <div class="row mt-3">
                  <div class="col-2 text-start">
                    <h4>Question:</h4>
                  </div>
                  <div class="col-10">
                    <span v-html="highlightedQuestion()"/>
                  </div>
                </div>
              </div>

              <div v-if="num_show != undefined ">
                <div class="row mt-3">
                  <div class="col-2 text-start">
                    <h4>Context:</h4>
                  </div>
                  <div class="col-10">
                    <span v-html="highlightedContext()"/>
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
import Vue from 'vue'
//import BadgePopover from '../BadgePopover'
// import { postQuery } from '../../api'
import context_json from './explainability_context.json'
// import question_json from './explainability_question.json'
import request_json from './explainability_request.json'

export default Vue.component("explain-output",{
  inject: ['currentResults'],
  data () {
     return {
      num_Maxshow : this.num_Maxshow,
      num_show : undefined,
      currentResults: this.currentResults,
  }
  },
  props:['test'],  //args should be the test json file
  components:{
    //BadgePopover // maybe useful
  },
  computed:{
    selectedSkills() {
      // remove None from skills list when send query
      return this.$store.state.skillOptions['qa'].selectedSkills.filter(skill => skill !== 'None')
    },
  },
  methods:{
    // write functions here

    postReq(method) {
      // Post the query with selected skills and given question, context
      // method for setting explain method : 'Attention','Scaled Attention','Simple Grad', 'Smooth Grad', 'Integrated Grad'
      this.waiting = true
      this.$store.dispatch('query', {
        question: this.$store.state.currentQuestion,
        inputContext: this.$store.state.currentContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.$store.state.skillOptions['qa'].maxResultsPerSkill,
          attrib_method: method
        }
      }).then(() => {
        this.failure = false,
        this.num_Maxshow =  request_json['explain_kwargs']['top_k']
        this.num_show = request_json['explain_kwargs']['top_k']
        console.log("Query successed! "),
        this.$store.state.currentQuestion = request_json['input'][0][0]
        this.$store.state.currentContext = request_json['input'][0][1]
        this.response = context_json //get the response from local json
     
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        this.waiting = false
      })
    },

    highLight(sentence,mode){ // add here skill param
      for (let i = 0; i<this.num_show;i++)
      {
        var currentWord = context_json['result']['attributions'][0][mode][i][1]
        let level = context_json['result']['attributions'][0][mode][i][2]
        level = level.toFixed(1) * 100
        level = Math.round(level) 
        if (level==0){
          level = 10
        }
        
        //using word color to highlight
        //var highLightedWord = '<mark class="bg-transparent text-opacity-'+ level.toString() +' text-danger">'+currentWord+'</mark>'
        //using background to highlight
        var highLightedWord = '<mark class="bg-warning p-2 text-dark bg-opacity-'+ level.toString() +' ">'+currentWord+'</mark>'

        console.log(highLightedWord)
        sentence =sentence.toLowerCase().replaceAll(context_json['result']['attributions'][0][mode][i][1],highLightedWord)   
      }
       return sentence

    },

    highlightedQuestion() {
    // Input:
    //   Question: strings,
    //   scores: a list of [word_idx,word,score]]
    // Output: 
    //   highlighted question
      return this.highLight(this.$store.state.currentQuestion,'question') 
    },

    highlightedContext() {
       return this.highLight(this.$store.state.currentContext,'context') 
    },

    changeShowNum(){
      var slider = document.getElementById("Range");
      this.num_show = slider.value;
    },

  },
})


</script>
