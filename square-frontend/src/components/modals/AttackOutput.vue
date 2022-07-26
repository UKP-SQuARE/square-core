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
                  <h1>Attack Methods</h1>
                  <hr/>
              </div>
            </div>

            <div class="row">
              <div class="col-4 text-start">
                  <h4>Method:</h4>
              </div>
              <div class="col-auto">
                  <button id="hotflip_btn" v-on:click="methodSelected('HotFlip')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Flips words in the input to change the Skill's prediction.">
                    HotFlip
                  </button>
              </div>
              <div class="col-auto">
                  <button id="Input_Red_btn" v-on:click="methodSelected('Input_Red')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Removes as many words from the input as possible without changing the Skill's prediction.">
                    Input Reduction
                  </button>
              </div>
              <div class="col-auto">
                  <button id="span_btn" v-on:click="methodSelected('span')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Selects a subspan of the context as new context.">
                    Sub-Span
                  </button>
              </div>
              <div class="col-auto">
                  <button id="topk_btn" v-on:click="methodSelected('topk')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="">
                    Top K
                  </button>
              </div>
            </div>

            <div v-if="hotflip_selected || inputred_selected || span_selected || topk_selected" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>Gradient Method:</h4>
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SimpleGrad" value="SimpleGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="SimpleGrad">Simple Gradients</label>
                </div>
                
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SmoothGrad" value="SmoothGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="SmoothGrad">Simple Gradients</label>
                </div>
                  
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="IntegratedGrad" value="IntegratedGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="IntegratedGrad">IntegratedGrad</label>
                </div>  
              </div>
            </div>

            <div v-if="hotflip_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># flips:</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="0" max="20" v-model="numFlips" class="form-range" id="numFlips" oninput="this.nextElementSibling.value = this.value">
                        <output ></output>
                    </div>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <label class="form-check-label" for="includeAns">Include Answer</label>
                        <input class="form-check-input" type="checkbox" id="includeAns">
                    </div>
                </div>
            </div>

            <div v-if="inputred_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># Reductions:</h4>
                </div>
                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="0" max="20" v-model="numReductions" class="form-range" id="numReductions" oninput="this.nextElementSibling.value = this.value">
                        <output ></output>
                    </div>
                </div>
            </div>

            <div v-if="span_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4>Length of sub-span:</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="0" max="20" v-model="lenSpan" class="form-range" id="lenSpan" oninput="this.nextElementSibling.value = this.value">
                        <output ></output>
                    </div>
                </div>
            </div>

            <div v-if="topk_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># top k:</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="0" max="20" v-model="numTopK" class="form-range" id="numTopK" oninput="this.nextElementSibling.value = this.value">
                        <output ></output>
                    </div>
                </div>
            </div>

            <div v-if="hotflip_selected" class="row mt-3"> <!-- HotFlip -->
              <div class="col-12">
                <button v-on:click="attack('HotFlip')" type="button" class="btn btn-outline-primary shadow" :disabled="waiting">
                    <span v-show="waiting" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attack Skill!
                </button>
              </div>
            </div> <!-- HotFlip -->

            <div v-if="inputred_selected" class="row mt-3"> <!-- InputReduction -->
              <div class="col-12">
                <button v-on:click="attack('Input_Red')" type="button" class="btn btn-outline-primary shadow" :disabled="waiting">
                    <span v-show="waiting" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attack Skill!
                </button>
                </div>
            </div> <!-- InputReduction -->

            <div v-if="span_selected" class="row mt-3"> <!-- Span -->
              <div class="col-12">
                <button v-on:click="attack('span')" type="button" class="btn btn-outline-primary shadow" :disabled="waiting">
                    <span v-show="waiting" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attack Skill!
                </button>
              </div>
            </div> <!-- Span -->

            <div v-if="topk_selected" class="row mt-3"> <!-- TopK -->
              <div class="col-12">
                <button v-on:click="attack('topk')" type="button" class="btn btn-outline-primary shadow" :disabled="waiting">
                    <span v-show="waiting" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attack Skill!
                </button>
              </div>
            </div> <!-- TopK -->

            <!-- Show question, flippedContext, and new answer  -->
            <div v-if="showHotFlipOutput" class="row mt-3">
              <hr/>
              <div class="col-4 text-start">
                  <h4>Question:</h4>
              </div>
              <div class="col-8 text-start">
                  <p>{{question}}</p>
              </div>
            </div> <!-- end question -->
            <div v-if="showHotFlipOutput" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>New Context:</h4>
              </div>
              <div class="col-8 text-start">
                  <span v-html="showNewContext()"/>
              </div>
            </div> <!-- end flippedContext -->
            <div v-if="showHotFlipOutput" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>New Answer:</h4>
              </div>
              <div class="col-8 text-start">
                  <p>{{newAnswer}}</p>
              </div>
            </div> <!-- end newAnswer -->
            
          </div> <!-- end container -->
        </div> <!-- end modal-body -->
      </div> <!-- end modal-content -->
    </div>  <!-- end modal-dialog -->
  </div> <!-- end modal -->
</template>

<script>
import Vue from 'vue'
import {tokenize} from 'string-punctuation-tokenizer'
import hotflip from './hotflip.json'
import inputred from './reduction.json'
import span from './span.json'
import topk from './topk.json'

// import input_red from './input_reduction_squad.json'
export default Vue.component("attack-output",{
  data () {
     return {
      num_Maxshow : this.num_Maxshow ,
      num_show : this.num_show ,
      gradient_way: 'SimpleGrad',
      includeAns: false,
      numFlips: 0,
      lenSpan: 0,
      numTopK: 0,
      numReductions: 0,

      hotflip_selected: false,
      inputred_selected: false,
      span_selected: false,
      topk_selected: false,

      question: '',
      newContext: "",
      newAnswer: "",
      waiting: false,
      showHotFlipOutput: false


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
    methodSelected(method){
      // remove active class from all buttons
      var buttons = document.getElementsByClassName('btn-outline-secondary')
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active')
      }
      if(method == 'HotFlip'){
        this.hotflip_selected = true;
        this.inputred_selected = false;
        this.span_selected = false;
        this.topk_selected = false;
        // set the class of the button to active
        document.getElementById('hotflip_btn').classList.add('active');
      }
      else if(method == 'Input_Red'){
        this.hotflip_selected = false;
        this.inputred_selected = true;
        this.span_selected = false;
        this.topk_selected = false;
        // set the class of the button to active
        document.getElementById('Input_Red_btn').classList.add('active');
      } else if(method == 'span'){
        this.hotflip_selected = false;
        this.inputred_selected = false;
        this.span_selected = true;
        this.topk_selected = false;
        // set the class of the button to active
        document.getElementById('span_btn').classList.add('active');
      } else if(method == 'topk'){
        this.hotflip_selected = false;
        this.inputred_selected = false;
        this.span_selected = false;
        this.topk_selected = true;
        // set the class of the button to active
        document.getElementById('topk_btn').classList.add('active');
      }
    },
    attack(method) {
      /* eslint-disable */
      this.waiting = true;
      if(method == 'HotFlip'){
        // make the call to the api

        var listContextTokens = tokenize({'text':  hotflip['context'], 'includePunctuation': true});
        var listFlips = hotflip['flips'];
        var listIndex = hotflip['indexes'];
        // for each flip change token from the context
        for(var i = 0; i < listFlips.length; i++){
          var flip = listFlips[i];
          var index = listIndex[i];
          var tooltip = 'data-bs-toggle="tooltip" data-bs-placement="top" title="'+listContextTokens[index]+'"';
          var highLightedWord = '<mark class="bg-success text-white"'+tooltip+'>'+flip[1]+'</mark>'
          listContextTokens[index] = highLightedWord;
        }
        // join tokens back to string
        this.newContext = listContextTokens.join(' ');
        this.question = hotflip['question'];
        this.newAnswer = hotflip['new_answer'];
        this.showHotFlipOutput = true;
        
      } else if(method == 'Input_Red'){
        // make the call to the api
        this.waiting = true;
        this.question = inputred['question'];
        this.newAnswer = inputred['answer'];
        this.showHotFlipOutput = true;
        this.newContext = inputred['remaining_context'];
      } else if(method == 'span'){
        this.waiting = true;
        this.question = span['question'];
        var context = span['context'];
        var keptSpan = span['span']; // [start, end]
        // split by white space
        var listContextTokens = context.split(/\s+/);
        var listKeptSpan = []
        var listLeftContext = []
        var listRightContext = []
        for(var i = 0; i < listContextTokens.length; i++){
          if (i < keptSpan[0]){ // left context
            listLeftContext.push(listContextTokens[i]);
          } else if(i > keptSpan[1]){ // right context
            listRightContext.push(listContextTokens[i]);
          } else{ // kept span
            listKeptSpan.push(listContextTokens[i]);
          }
        }
        // Line-through the left context
        var leftContextHtml= '<span class="text-decoration-line-through text-secondary">'+listLeftContext.join(' ')+'</span>';
        // Line-through the right context
        var rightContextHtml= '<span class="text-decoration-line-through text-secondary">'+listRightContext.join(' ')+'</span>';
        // highlight the kept span
        var keptSpanHtml = '<span class="bg-success text-white">'+listKeptSpan.join(' ')+'</span>';
        // join tokens back to string
        this.newContext = leftContextHtml+keptSpanHtml+rightContextHtml;
        this.newAnswer = span['answer'];
        this.showHotFlipOutput = true;
      } else if(method == 'topk'){
        this.waiting = true;
        this.question = topk['question'];
        this.newAnswer = topk['new_answer'];
        this.showHotFlipOutput = true;
        var listIndex = topk['indexes'];
        var listContextTokens = topk['context'].split(/\s+/);
        var listKeptSpan = []
        var contextHtml = '';
        for(var i = 0; i < listContextTokens.length; i++){
          if(listIndex.includes(i)){
            // highlight the kept span
            contextHtml += '<span class="bg-success text-white">'+listContextTokens[i]+' </span>';
          } else{
            contextHtml += '<span class="text-decoration-line-through text-secondary">'+listContextTokens[i]+' </span>';
          }
        }
        this.newContext = contextHtml;
      }
      this.waiting = false;
      // this.waiting = true
      // this.$store.dispatch('query', {
      //   question: this.$store.state.currentQuestion,
      //   inputContext: this.$store.state.currentContext,
      //   options: {
      //     selectedSkills: this.selectedSkills,
      //     maxResultsPerSkill: this.$store.state.skillOptions['qa'].maxResultsPerSkill,
      //     attrib_method: method
      //   }
      // }).then(() => {
        // this.failure = false,
        // this.num_Maxshow =  request_json['explain_kwargs']['top_k']
        // this.num_show = request_json['explain_kwargs']['top_k']
        // console.log("Query successed! "),
        // this.$store.state.currentQuestion = request_json['input'][0][0]
        // this.$store.state.currentContext = request_json['input'][0][1]
        // this.response = context_json //get the response from local json
      // }).catch(() => {
      //   this.failure = true
      // }).finally(() => {
      //   this.waiting = false
      // })
    },
    showNewContext(){
      return this.newContext;
    },
    
  },
})
</script>