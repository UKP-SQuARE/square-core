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
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-frown" viewBox="0 0 16 16">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                  <path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z"/>
                </svg>
              </div>
  
              <div class="row">
                <div class="col-12">
                    <h1>BertViz
                      <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-map" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M15.817.113A.5.5 0 0 1 16 .5v14a.5.5 0 0 1-.402.49l-5 1a.502.502 0 0 1-.196 0L5.5 15.01l-4.902.98A.5.5 0 0 1 0 15.5v-14a.5.5 0 0 1 .402-.49l5-1a.5.5 0 0 1 .196 0L10.5.99l4.902-.98a.5.5 0 0 1 .415.103zM10 1.91l-4-.8v12.98l4 .8V1.91zm1 12.98 4-.8V1.11l-4 .8v12.98zm-6-.8V1.11l-4 .8v12.98l4-.8z"/>
                      </svg>
                      </h1>
                    <hr/>
                </div>
              </div>
  
              <div class="container-fluid text-center">
                <div class="row g-2 gy-2">
                  <div class="col-md-2 text-right">
                      <h4>Method:</h4>
                  </div>
                  <div class="col btn-group flex-wrap" role="group" aria-label="Basic example">
                    <button id="bertviz_btn" v-on:click="postReq('bertviz')" type="button" class="btn btn-outline-primary" :disabled="waiting_bertviz">
                      <span v-show="waiting_bertviz" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Bertviz
                    </button>
                  </div>
                </div> <!--  end method row -->
              </div>

              <div v-if="show_bertviz">
                <div class="row mt-3" v-for="(skillResult, index) in this.$store.state.currentResults" :key="index">
                  <div class="col-12">
                    <hr/>
                    <h4>{{ skillResult.skill.name }}</h4>
                  </div>
  
                  <div v-if="show_bertviz"> <!-- show bertviz -->
                    <div class="row mt-3">
                      <div class="col-18">
                        <div>
                          <iframe :srcdoc="BertViz_html(index)" frameborder="0" width="50%" height="500px" ></iframe>
                         </div>
                      </div>
                    </div>
                  </div> <!-- end show bertviz -->
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
  
  export default Vue.component("explain-output",{
    inject: ['currentResults'],
    data () {
       return {
        waiting_bertviz: false,
        show_bertviz: false,
        failure: false,
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
  
        this.show_bertviz = false;
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
              mode: 'all', // can be 'all', 'question', 'context'
            }
          }
        }).then(() => {
          this.failure = false,
          this.num_show = 3
          this.show_bertviz = true;
          // add class active to the button method+"_btn"
          document.getElementById(method+"_btn").classList.add("active");
          // the tokenizer used by the API is a bit different from the one used in the frontend,
        }).catch(() => {
          this.failure = true
        }).finally(() => {
          // switch the waiting_* variables to false to stop loading spinner
          this.stopSpinner(method);
        })
      },
      stopSpinner(method){
        this.changeSpinnerStatus(method, false);
      },
      runSpinner(method){
        this.changeSpinnerStatus(method, true);
      },
      changeSpinnerStatus(method, value){
        switch(method){
          case 'bertviz':
            this.waiting_bertviz = value;
            break;
          }
      },
  
      BertViz_html(idx) {
        var json =this.$store.state.currentResults[idx].predictions[0].bertviz;
        let obj = JSON.parse(JSON.stringify(json));    // maybe there is no need to stringify and parse.Needs testing!!!!
        return obj
      },

  
      close(){
        this.show_bertviz = false;
        // remove activate class from all buttons
        var btn_list = document.getElementsByClassName('btn-outline-primary');
        for (var i = 0; i < btn_list.length; i++) {
          btn_list[i].classList.remove('active');
        }
      }
  
      
    },
  })

  </script>
  