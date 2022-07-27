<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" @click.self="close">
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
              <div class="col-auto">
                <button id="attention_btn" v-on:click="postReq('attention')" type="button" class="btn btn-outline-primary" :disabled="waiting_attention">
                  <span v-show="waiting_attention" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attention
                </button>
              </div>
              <div class="col-auto">
                <button id="scaled_attention_btn" v-on:click="postReq('scaled_attention')" type="button" class="btn btn-outline-primary" :disabled="waiting_scaled_attention">
                  <span v-show="waiting_scaled_attention" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Scaled Attention
                </button>
              </div>
              <div class="col-auto">
                <button id="simple_grads_btn" v-on:click="postReq('simple_grads')" type="button" class="btn btn-outline-primary" :disabled="waiting_simple_grads">
                  <span v-show="waiting_simple_grads" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Simple Gradients
                </button>
              </div>
              <div class="col-auto">
                <button id="smooth_grads_btn" v-on:click="postReq('smooth_grads')"  type="button" class="btn btn-outline-primary" :disabled="waiting_smooth_grads">
                  <span v-show="waiting_smooth_grads" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Smooth Gradients
                </button>
              </div>
              <div class="col-auto">
                <button id="integrated_grads_btn" v-on:click="postReq('integrated_grads')"  type="button" class="btn btn-outline-primary" :disabled="waiting_integrated_grads">
                  <span v-show="waiting_integrated_grads" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Integrated Gradients
                </button>
              </div>
            </div>

            <div v-if="show_saliency_map" class="slidecontainer">
              <div class="row mt-3">
                <div class="col-6 text-start">
                  <h4>Showing the top {{num_show}} most important words</h4>
                </div>
                <div class="col-6">
                  <input type="range" min="1" :max="num_Maxshow" value="3" class="form-range" id="Range" @click="changeShowNum()"  >
                </div>
              </div>
            </div>
            
            <div v-if="show_saliency_map">
              <div class="row mt-3" v-for="(skillResult, index) in this.$store.state.currentResults" :key="index">
                <div class="col-12">
                  <h4>{{ skillResult.skill.name }}</h4>
                  <hr/>
                </div>

                <div v-if="show_saliency_map"> <!-- show question -->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Question:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="highlightedQuestion(index)"/>
                    </div>
                  </div>
                </div> <!-- end show question -->

                <div v-if="show_saliency_map"> <!-- show context-->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Context:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="highlightedContext(index)"/>
                    </div>
                  </div>
                </div> <!-- end show context -->

                <div v-if="show_saliency_map"> <!-- show answer-->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Answer:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="showAnswer(index)"/>
                    </div>
                  </div>
                </div> <!-- end show answer -->

              </div> <!-- end for loop -->
            </div>
            

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
// eslint-disable-next-line
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  // eslint-disable-next-line
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

import Vue from 'vue'

export default Vue.component("explain-output",{
  inject: ['currentResults'],
  data () {
     return {
      num_Maxshow: undefined,
      num_show: undefined,
      waiting_attention: false,
      waiting_scaled_attention: false,
      waiting_simple_grads: false,
      waiting_smooth_grads: false,
      waiting_integrated_grads: false,
      show_saliency_map: false,
      }
  },
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
    postReq(method) {
      // num words in context
      var numQuestionWords = this.tokenize(this.$store.state.currentQuestion).length;
      // num_Maxshow for explain method is the min(numWords, numContextWords)
      var numContextWords = this.tokenize(this.$store.state.currentContext).length;
      this.num_Maxshow =  Math.min(numQuestionWords, numContextWords);
      // method for setting explain method : 'attention', 'scaled_attention', 'simple_grads', 'smooth_grads', 'integrated_grads'      
      // remove class active from all buttons
      var btn_list = document.getElementsByClassName('btn-outline-primary');
      for (var i = 0; i < btn_list.length; i++) {
        btn_list[i].classList.remove('active');
      }
      // switch the waiting_* variables to true to show the loading spinner
      switch(method){
        case 'attention':
          this.waiting_attention = true;
          break;
        case 'scaled_attention':
          this.waiting_scaled_attention = true;
          break;
        case 'simple_grads':
          this.waiting_simple_grads = true;
          break;
        case 'smooth_grads':
          this.waiting_smooth_grads = true;
          break;
        case 'integrated_grads':
          this.waiting_integrated_grads = true;
          break;
      }
      this.show_saliency_map = false;
      this.$store.dispatch('query', {
        question: this.$store.state.currentQuestion,
        inputContext: this.$store.state.currentContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.$store.state.skillOptions['qa'].maxResultsPerSkill,
          explain_kwargs: {
            method: method,
            top_k: this.num_Maxshow,
            mode: 'all' // can be 'all', 'question', 'context'
          }
        }
      }).then(() => {
        this.failure = false,
        this.num_show = 3
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        // switch the waiting_* variables to false to stop loading spinner
        switch(method){
          case 'attention':
            this.waiting_attention = false;
            break;
          case 'scaled_attention':
            this.waiting_scaled_attention = false;
            break;
          case 'simple_grads':
            this.waiting_simple_grads = false;
            break;
          case 'smooth_grads':
            this.waiting_smooth_grads = false;
            break;
          case 'integrated_grads':
            this.waiting_integrated_grads = false;
            break;
        }
        this.show_saliency_map = true;
        // add class active to the button method+"_btn"
        document.getElementById(method+"_btn").classList.add("active");

      })
    },

    tokenize(sentence){
      // tokenize a sentence by whitespace and punctuation
      // input: "We've got a lot of data to work with, Let's do some analysis."
      // output: ["We've", "got", "a", "lot", "of", "data", "to", "work", "with", ",", "Let's", "do", "some", "analysis", "."]
      var sentence_list = sentence.split(/\s+/);
      // for each word in sentence_list
      var listWords = [];
      for (var i = 0; i < sentence_list.length; i++) {
        var word = sentence_list[i];
        // if word has . , ! ? ; ( ) [ ]
        // eslint-disable-next-line
        if (word.match(/[.,!?;\-\_()\[\]]/)) {
          console.log("word has punctuation: " + word);
          if (word.includes(".")) {
            let w2 = word.replace(".","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push(".");
          }
          if (word.includes("!")) {
            let w2 = word.replace("!","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push("!");
          } 
          if (word.includes(",")) {
            let w2 = word.replace(",","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push(",");
          } 
          if (word.includes("?")) {
            let w2 = word.replace("?","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push("?");
          } 
          if (word.includes(";")) {
            let w2 = word.replace(";","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push(";");
          } 
          if (word.includes("-")) {
            let w2 = word.replace("-","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push("-");
          }
          if (word.includes("_")) {
            let w2 = word.replace("_","")
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push("_");
          }
          if (word.includes("(")) {
            if (word.includes(")")) {
              let w2 = word.replace("(","").replace(")","");
              listWords.push("(");
              // if w2 is not empty, add w2 to listWords
              if (w2 !== "") {
                listWords.push(w2);
              }
              listWords.push(")");
            } else {
              let w2 = word.replace("(","");
              // if w2 is not empty, add w2 to listWords
              if (w2 !== "") {
                listWords.push(w2);
              }
              listWords.push("(");
            }
          } 
          if (word.includes(")") && !word.includes("(")) {
            let w2 = word.replace(")","");
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push(")");
          }
          if (word.includes("[")) {
            if (word.includes("]")) {
              listWords.push("[");
              let w2 = word.replace("[","").replace("]","");
              // if w2 is not empty, add w2 to listWords
              if (w2 !== "") {
                listWords.push(w2);
              }
              listWords.push("]");
            } else {
              let w2 = word.replace("[","");
              // if w2 is not empty, add w2 to listWords
              if (w2 !== "") {
                listWords.push(w2);
              }
              listWords.push("[");
            }
          } 
          if (word.includes("]") && !word.includes("[")) {
            let w2 = word.replace("]","");
            // if w2 is not empty, add w2 to listWords
            if (w2 !== "") {
              listWords.push(w2);
            }
            listWords.push("]");
          }
        } else {
          listWords.push(word);
        }
      }
      console.log(listWords)
      return listWords;
    },

    highLight(sentence,attributions){ // add here skill param
      var listWords = this.tokenize(sentence);
      // console.log(listWords);
      // var listWords = tokenize({'text': sentence, 'includePunctuation': true});
      // log to console listWords
      // var listWords = sentence.split(' ');
      var highlightedSentence = "";
      // iterate over attributions to normalize the scores to [0,1]
      var maxScore = Math.max.apply(Math, attributions.map(function(o){return o[2];}));
      var minScore = Math.min.apply(Math, attributions.map(function(o){return o[2];}));
      var scoreRange = maxScore - minScore;
      attributions.forEach(function(attribution){
        attribution[2] = (attribution[2] - minScore)/scoreRange;
      });

      for (let i = 0; i<this.num_show;i++) {
        var wordIdx = attributions[i][0]
        var currentWord = attributions[i][1]
        var level = attributions[i][2]
        level = level.toFixed(1) * 100;
        level = Math.round(level) ;
        if (level==0) {
          level = 10;
        }
        level = level/100;
        level = level.toString()
        // tooltip the word with the level
        var tooltip = 'data-bs-toggle="tooltip" data-bs-placement="top" title="'+level+'"';
        var highLightedWord = '<mark class="bg-warning p-2 text-dark" '+tooltip+' style="--bs-bg-opacity: '+ level +'">'+currentWord+'</mark>'
        listWords[wordIdx] = highLightedWord;
      }
      for (let i = 0; i<listWords.length;i++) {
        highlightedSentence += listWords[i] + " ";
      }
      return highlightedSentence

    },

    highlightedQuestion(idx) {
    // Input:
    //   Question: strings,
    //   attributions: a list of [word_idx,word,score]]
    // Output: 
    //   highlighted question
      return this.highLight(this.$store.state.currentQuestion,
                            this.$store.state.currentResults[idx].predictions[0].attributions.question) 
    },

    highlightedContext(idx) {
      return this.highLight(this.$store.state.currentContext,
                            this.$store.state.currentResults[idx].predictions[0].attributions.context)
    },

    showAnswer(idx) {
      return this.$store.state.currentResults[idx].predictions[0].prediction_output.output
    },

    changeShowNum(){
      var slider = document.getElementById("Range");
      this.num_show = slider.value;
    },

    close(){
      this.show_saliency_map = false;
      this.num_Maxshow = undefined;
      // remove activate class from all buttons
      var btn_list = document.getElementsByClassName('btn-outline-primary');
      for (var i = 0; i < btn_list.length; i++) {
        btn_list[i].classList.remove('active');
      }
    }

    
  },
})


</script>
