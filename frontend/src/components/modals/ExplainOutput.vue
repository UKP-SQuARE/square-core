<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" @click.self="close">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click.self="close" />
        </div>
        <div class="modal-body">
          <div class="container text-center">
            <div class="alert alert-warning" v-if="this.$store.state.loadingExplainability" role="alert">
              It's taking a bit longer than usual to generate your output... Please hang in there.
            </div>
            <div class="alert alert-warning" v-if="failure" :dismissible="true" role="alert">
              An error occurred
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-frown"
                viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z" />
              </svg>
            </div>

            <div class="row">
              <div class="col-12">
                <h1>Saliency Map
                  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-map"
                    viewBox="0 0 16 16">
                    <path fill-rule="evenodd"
                      d="M15.817.113A.5.5 0 0 1 16 .5v14a.5.5 0 0 1-.402.49l-5 1a.502.502 0 0 1-.196 0L5.5 15.01l-4.902.98A.5.5 0 0 1 0 15.5v-14a.5.5 0 0 1 .402-.49l5-1a.5.5 0 0 1 .196 0L10.5.99l4.902-.98a.5.5 0 0 1 .415.103zM10 1.91l-4-.8v12.98l4 .8V1.91zm1 12.98 4-.8V1.11l-4 .8v12.98zm-6-.8V1.11l-4 .8v12.98l4-.8z" />
                  </svg>
                </h1>
                <hr />
              </div>
            </div>

            <div class="container-fluid text-center">
              <div class="row g-2 gy-2">
                <div class="col-md-2 text-right">
                  <h4>Method:</h4>
                </div>
                <div class="col btn-group flex-wrap" role="group" aria-label="Basic example">
                  <button id="attention_btn" v-on:click="postReq('attention')" type="button"
                    class="btn btn-outline-primary" :disabled="waiting_attention">
                    <span v-show="waiting_attention" class="spinner-border spinner-border-sm"
                      role="status" />&nbsp;Attention
                  </button>
                  <button v-if="scaledAttentionAvailable" id="scaled_attention_btn"
                    v-on:click="postReq('scaled_attention')" type="button" class="btn btn-outline-primary"
                    :disabled="waiting_scaled_attention">
                    <span v-show="waiting_scaled_attention" class="spinner-border spinner-border-sm"
                      role="status" />&nbsp;Scaled Attention
                  </button>
                  <button id="simple_grads_btn" v-on:click="postReq('simple_grads')" type="button"
                    class="btn btn-outline-primary" :disabled="waiting_simple_grads">
                    <span v-show="waiting_simple_grads" class="spinner-border spinner-border-sm"
                      role="status" />&nbsp;Simple Gradients
                  </button>
                  <button id="smooth_grads_btn" v-on:click="postReq('smooth_grads')" type="button"
                    class="btn btn-outline-primary" :disabled="waiting_smooth_grads">
                    <span v-show="waiting_smooth_grads" class="spinner-border spinner-border-sm"
                      role="status" />&nbsp;Smooth Gradients
                  </button>
                  <button id="integrated_grads_btn" v-on:click="postReq('integrated_grads')" type="button"
                    class="btn btn-outline-primary" :disabled="waiting_integrated_grads">
                    <span v-show="waiting_integrated_grads" class="spinner-border spinner-border-sm"
                      role="status" />&nbsp;Integrated Gradients
                  </button>
                </div>
              </div> <!--  end method row -->
            </div>


            <div v-if="show_saliency_map" class="slidecontainer">
              <div class="row mt-3">
                <div class="col-6 text-start">
                  <h4>Showing the top {{ num_show }} most important words</h4>
                </div>
                <div class="col-6">
                  <input type="range" min="1" :max="num_Maxshow" value="3" class="form-range" id="Range"
                    @click="changeShowNum()">
                </div>
              </div>
            </div>

            <div v-if="show_saliency_map">
              <div class="row mt-3" v-for="(skillResult, index) in this.$store.state.currentResults" :key="index">
                <div class="col-12">
                  <hr />
                  <h4>{{ skillResult.skill.name }}</h4>
                </div>

                <div v-if="show_saliency_map"> <!-- show question -->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Question:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="highlightedQuestion(index)" />
                    </div>
                  </div>
                </div> <!-- end show question -->

                <div v-if="show_saliency_map"> <!-- show context-->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Context:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="highlightedContext(index)" />
                    </div>
                  </div>
                </div> <!-- end show context -->

                <div v-if="show_saliency_map"> <!-- show answer-->
                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Answer:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="showAnswer(index)" />
                    </div>
                  </div>
                </div> <!-- end show answer -->

              </div> <!-- end for loop -->
            </div> <!-- end show saliency map -->


          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>


import Vue from 'vue'
import { tokenize } from 'string-punctuation-tokenizer'

export default Vue.component("explain-output", {
  inject: ['currentResults'],
  props: ['selectedSkills'],
  data() {
    return {
      num_Maxshow: undefined,
      num_show: undefined,
      waiting_attention: false,
      waiting_scaled_attention: false,
      waiting_simple_grads: false,
      waiting_smooth_grads: false,
      waiting_integrated_grads: false,
      show_saliency_map: false,
      failure: false,
    }
  },
  components: {
    //BadgePopover // maybe useful
  },
  computed: {
    scaledAttentionAvailable() {
      if (this.$store.state.currentResults[0].skill.skill_type === 'multiple-choice') {
        return false
      } else {
        return true
      }
    },
  },
  methods: {
    postReq(method) {
      // reset UI
      this.failure = false;
      // remove class active from all buttons
      var btn_list = document.getElementsByClassName('btn-outline-primary');
      for (var i = 0; i < btn_list.length; i++) {
        btn_list[i].classList.remove('active');
      }

      // real method starts here
      // get the context and the top_k words to show
      var context = this.$store.state.currentContext
      var skill = this.$store.state.currentResults[0].skill
      if (skill.skill_type == 'span-extraction' && !skill.skill_settings.requiresContext) { // for ODQA
        context = this.$store.state.currentResults[0].predictions[0].prediction_documents[0].document
      }
      var numContextWords = tokenize({ 'text': context, 'includePunctuation': true }).length;
      var numQuestionWords = tokenize({ 'text': this.$store.state.currentQuestion, 'includePunctuation': true }).length;
      this.num_Maxshow = Math.max(numQuestionWords, numContextWords);

      this.show_saliency_map = false;
      this.runSpinner(method);
      // api call
      this.$store.dispatch('query', {
        question: this.$store.state.currentQuestion,
        inputContext: context,
        choices: this.$store.state.currentChoices,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.$store.state.skillOptions['qa'].maxResultsPerSkill,
          explain_kwargs: {
            method: method,
            top_k: this.num_Maxshow,
            mode: 'all', // can be 'all', 'question', 'context'
          }
        }
      }).then(() => {
        this.failure = false,
          this.num_show = 3
        this.show_saliency_map = true;
        // add class active to the button method+"_btn"
        document.getElementById(method + "_btn").classList.add("active");
        // the tokenizer used by the API is a bit different from the one used in the frontend,
        // so update num_Maxshow with the real number of words in the context
        this.num_Maxshow = this.$store.state.currentResults[0].predictions[0].attributions.topk_context_idx.length;
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        // switch the waiting_* variables to false to stop loading spinner
        this.stopSpinner(method);
      })
    },
    stopSpinner(method) {
      this.changeSpinnerStatus(method, false);
    },
    runSpinner(method) {
      this.changeSpinnerStatus(method, true);
    },
    changeSpinnerStatus(method, value) {
      switch (method) {
        case 'attention':
          this.waiting_attention = value;
          break;
        case 'scaled_attention':
          this.waiting_scaled_attention = value;
          break;
        case 'simple_grads':
          this.waiting_simple_grads = value;
          break;
        case 'smooth_grads':
          this.waiting_smooth_grads = value;
          break;
        case 'integrated_grads':
          this.waiting_integrated_grads = value;
          break;
      }
    },
    highLight(topk_idx, attributions) { // add here skill param
      var listWords = [];
      for (var i = 0; i < attributions.length; i++) {
        listWords.push(attributions[i][1]);
      }

      var highlightedSentence = "";
      // iterate over attributions to normalize the scores to [0,1]
      var maxScore = Math.max.apply(Math, attributions.map(function (o) { return o[2]; }));
      var minScore = Math.min.apply(Math, attributions.map(function (o) { return o[2]; }));
      var scoreRange = maxScore - minScore;
      attributions.forEach(function (attribution) {
        attribution[3] = (attribution[2] - minScore) / scoreRange;
      });
      var max_show = Math.min(this.num_show, attributions.length);
      for (let i = 0; i < max_show; i++) {
        var token_idx = topk_idx[i]
        var currentWord = attributions[token_idx][1]
        var level = attributions[token_idx][3]
        level = level.toFixed(1) * 100;
        level = Math.round(level);
        if (level == 0) {
          level = 10;
        }
        level = level / 100;
        level = level.toString()

        // tooltip the word with the level
        var tooltip = 'data-bs-toggle="tooltip" data-bs-placement="top" title="' + attributions[token_idx][2] + '"';
        var highLightedWord = '<mark class="bg-warning text-dark" ' + tooltip + ' style="--bs-bg-opacity: ' + level + '">' + currentWord + '</mark>'
        listWords[token_idx] = highLightedWord;
      }
      for (let i = 0; i < listWords.length; i++) {
        highlightedSentence += listWords[i] + " ";
      }
      return highlightedSentence

    },

    highlightedQuestion(idx) {
      return this.highLight(this.$store.state.currentResults[idx].predictions[0].attributions.topk_question_idx,
        this.$store.state.currentResults[idx].predictions[0].attributions.question_tokens,
      );
    },

    highlightedContext(idx) {
      return this.highLight(this.$store.state.currentResults[idx].predictions[0].attributions.topk_context_idx,
        this.$store.state.currentResults[idx].predictions[0].attributions.context_tokens,
      );
    },

    showAnswer(idx) {
      return this.$store.state.currentResults[idx].predictions[0].prediction_output.output
    },

    changeShowNum() {
      var slider = document.getElementById("Range");
      this.num_show = slider.value;
    },

    close() {
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
