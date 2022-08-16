<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true"  @click.self="close">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"  @click.self="close"/>
        </div>
        <div class="modal-body">
          <div class="container text-center">
            <div class="alert alert-warning" v-if="failure" :dismissible="true" role="alert">
              An error occurred 
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-frown" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z"/>
              </svg>
            </div>

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
                  <button id="hotflip_btn" v-on:click="methodSelected('hotflip')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Flips words in the input to change the Skill's prediction.">
                    HotFlip
                  </button>
              </div>
              <div class="col-auto">
                  <button id="input_reduction_btn" v-on:click="methodSelected('input_reduction')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Removes as many words from the input as possible without changing the Skill's prediction.">
                    Input Reduction
                  </button>
              </div>
              <div class="col-auto">
                  <button id="sub_span_btn" v-on:click="methodSelected('sub_span')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Selects a subspan of the context as new context.">
                    Sub-Span
                  </button>
              </div>
              <div class="col-auto">
                  <button id="topk_tokens_btn" v-on:click="methodSelected('topk_tokens')" type="button" class="btn btn-outline-secondary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="">
                    Top K
                  </button>
              </div>
            </div>

            <div v-if="hotflip_selected || span_selected || topk_selected" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>Attribution Method:</h4>
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SimpleGrad" value="simple_grads" v-model="saliencyMethod"/>
                  <label class="form-check-label" for="SimpleGrad">Simple Gradients</label>
                </div>
                
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SmoothGrad" value="smooth_grads" v-model="saliencyMethod"/>
                  <label class="form-check-label" for="SmoothGrad">Smooth Gradients</label>
                </div>
                  
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="IntegratedGrad" value="integrated_grads" v-model="saliencyMethod"/>
                  <label class="form-check-label" for="IntegratedGrad">IntegratedGrad</label>
                </div>  
              </div>

              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="attention" value="attention" v-model="saliencyMethod"/>
                  <label class="form-check-label" for="attention">Attention</label>
                </div>  
              </div>
            </div>

            <div v-if="hotflip_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># flips: {{numFlips}}</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="1" max="10" v-model="numFlips" class="form-range" id="numFlips" @click="showAttack()">
                    </div>
                </div>

            </div>

            <div v-if="inputred_selected" class="row mt-3">
                <div class="col-4 text-start">
                  <h4># Reductions: {{numReductions}}</h4>
                </div>
                <div class="col-auto">
                  <div class="form-check form-switch">
                    <input type="range" min="1" :max="maxReductions" v-model="numReductions" class="form-range" id="numReductions" @click="showAttack()">
                  </div>
                </div>
            </div>

            <div v-if="span_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4>Length of sub-span: {{lenSpan}}</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="2" :max="maxLenSpan" v-model="lenSpan" v-on:click="attack()" class="form-range" id="lenSpan">
                    </div>
                </div>
            </div>

            <div v-if="topk_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># top k: {{numTopK}}</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <input type="range" min="1" :max="maxTopK" v-model="numTopK" v-on:click="attack()" class="form-range" id="numTopK">
                    </div>
                </div>
            </div>

            <div v-if="showAttackBtn" class="row mt-3"> <!-- HotFlip -->
              <div class="col-12">
                <button v-on:click="attack()" type="button" class="btn btn-outline-primary shadow" :disabled="waiting">
                    <span v-show="waiting" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Attack Skill!
                </button>
              </div>
            </div> <!-- HotFlip -->

            <!-- Show question, flippedContext, and new answer  -->
            <div v-if="showAttackOutput" class="d-flex row mt-3">
              <hr/>
              <div class="col-4 text-start">
                  <h4>Question:</h4>
              </div>
              <div class="col-8 text-start">
                  <span v-html="newQuestion"/>
              </div>
            </div> <!-- end question -->
            <div v-if="showAttackOutput" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>New Context:</h4>
              </div>
              <div class="col-8 text-start">
                  <span v-html="newContext"/>
              </div>
            </div> <!-- end flippedContext -->
            <div v-if="showAttackOutput" class="row mt-3 align-items-center">
                <div class="col-4 text-start">
                  <h4>New Answer:</h4>
                </div>
                <div class="col-3 text-start vertical-center">
                    {{newAnswer}}
                </div>
                <div class="col-2 text-start ">
                    <h4>Old Answer:</h4>
                </div>
                <div class="col-3 text-start">
                    {{this.$store.state.currentResults[0].predictions[0]['prediction_output']['output']}}
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

export default Vue.component("attack-output",{
  data () {
     return {
      method: undefined,
      saliencyMethod: 'simple_grads',
      numFlips: 1,
      lenSpan: 3,
      maxLenSpan: this.$store.state.currentContext.split(/\s+/).length,
      numTopK: 1,
      maxTopK: this.$store.state.currentContext.split(/\s+/).length,
      numReductions: 1,
      maxReductions: 1,

      hotflip_selected: false,
      inputred_selected: false,
      span_selected: false,
      topk_selected: false,

      newQuestion: "",
      newContext: "",
      newAnswer: "",
      waiting: false,
      showHotFlipOutput: false,
      showAttackBtn: false,
      showAttackOutput: false,
      failure: false,
    }
  },
  computed:{
    selectedSkills() {
      // remove None from skills list when send query
      return this.$store.state.skillOptions['qa'].selectedSkills.filter(skill => skill !== 'None')
    },
  },
  methods:{
    methodSelected(method){
      this.method = method;
      this.showAttackBtn = true;
      // remove active class from all buttons
      var buttons = document.getElementsByClassName('btn-outline-secondary')
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active')
      }
      if(method == 'hotflip'){
        this.setAllButtonsUnselected();
        this.hotflip_selected = true;
        document.getElementById('hotflip_btn').classList.add('active');
      } else if(method == 'input_reduction'){
        this.setAllButtonsUnselected();
        this.inputred_selected = true;
        document.getElementById('input_reduction_btn').classList.add('active');
        this.saliencyMethod = 'attention';
      } else if(method == 'sub_span'){
        this.setAllButtonsUnselected();
        this.span_selected = true;
        document.getElementById('sub_span_btn').classList.add('active');
      } else if(method == 'topk_tokens'){
        this.setAllButtonsUnselected();
        this.topk_selected = true;
        document.getElementById('topk_tokens_btn').classList.add('active');
      }
    },
    setAllButtonsUnselected(){
      this.hotflip_selected = false;
      this.inputred_selected = false;
      this.span_selected = false;
      this.topk_selected = false;
    },
    attack() {
      /* eslint-disable */
      this.waiting = true;
      this.$store.dispatch('attack', {
        question: this.$store.state.currentQuestion,
        inputContext: this.$store.state.currentContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.$store.state.skillOptions['qa'].maxResultsPerSkill,
          attack_kwargs: this.prepareAttackKwargs(),
        }
      }).then(() => {
        this.failure = false
        console.log('success');
        this.showAttackOutput = true;
        this.showAttack();
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        // switch the waiting_* variables to false to stop loading spinner
        this.waiting = false;
      })
    },
    prepareAttackKwargs(){
      var attack_kwargs = {method: this.method, saliency_method: this.saliencyMethod,}
      // if method is hotflip, add max_flips
      if(this.method == 'hotflip'){
        attack_kwargs['max_flips'] = 10;
      }
      // if method is input_reduction, add max_reductions
      if(this.method == 'input_reduction'){
        // tokenize currentQuestion
        this.maxReductions = this.$store.state.currentQuestion.split(' ').length;
        attack_kwargs['max_reductions'] = this.maxReductions;
      }
      // if method is sub_span, add max_tokens
      if(this.method == 'sub_span'){
        attack_kwargs['max_tokens'] = parseInt(this.lenSpan);
      }
      // if method is topk_tokens, add max_tokens
      if(this.method == 'topk_tokens'){
        attack_kwargs['max_tokens'] = parseInt(this.numTopK);
      }
      return attack_kwargs;
    },
    showAttack(){
      console.log('show attack');
      if (this.method == 'hotflip'){
        this.prepareHotFlipAttack();
      } else if (this.method == 'input_reduction'){
        this.prepareInputReductionAttack();
      } else if (this.method == 'sub_span'){
        this.prepareSubSpanAttack();
      } else if (this.method == 'topk_tokens'){
        this.prepareTopKAttack();
      }
    },
    prepareHotFlipAttack(){
      var indices = this.$store.state.attackResults[0].adversarial.indices;
      var context = this.$store.state.attackResults[0].predictions[0].prediction_documents[0].document;
      var listContexts = []
      for (var i = 1; i < this.$store.state.attackResults[0].predictions.length; i++) {
        var prediction = this.$store.state.attackResults[0].predictions[i];
        listContexts.push(prediction.prediction_documents[0].document);
      }
      // tokenize the context by white space
      var tokenizedContext = context.split(/\s+/);
      // flip context token with indices
      for (var flipIdx=0; flipIdx<this.numFlips; flipIdx++){
        var newContext = listContexts[flipIdx];
        var tokenizedNewContext = newContext.split(/\s+/);
        var oldToken = tokenizedContext[indices[flipIdx]];
        var newToken = tokenizedNewContext[indices[flipIdx]];
        
        var tooltip = 'data-bs-toggle="tooltip" data-bs-placement="top" title="'+oldToken+'"';
        var highLightedToken = '<mark class="bg-success text-white"'+tooltip+'>'+newToken+'</mark>'
        tokenizedContext[indices[flipIdx]] = highLightedToken
      }
      this.newContext = tokenizedContext.join(' ');
      this.newAnswer = this.$store.state.attackResults[0].predictions[this.numFlips].prediction_output['output'];
      this.newQuestion = this.$store.state.attackResults[0].predictions[this.numFlips].question;
    },
    prepareInputReductionAttack(){
      var indices = this.$store.state.attackResults[0].adversarial.indices;
      var oldQuestion = this.$store.state.attackResults[0].predictions[0].question;
      // tokenize the question by white space
      var tokenizedOldQuestion = oldQuestion.split(/\s+/);
      // flip context token with indices
      for (var redIdx=0; redIdx<this.numReductions; redIdx++){
        var oldToken = tokenizedOldQuestion[indices[redIdx]];
        
        var highLightedToken = '<s><mark class="bg-danger text-white">'+oldToken+'</mark></s>'
        tokenizedOldQuestion[indices[redIdx]] = highLightedToken
      }
      this.newContext = this.$store.state.attackResults[0].predictions[this.numReductions].prediction_documents[0].document;
      this.newAnswer = this.$store.state.attackResults[0].predictions[this.numReductions].prediction_output['output'];
      this.newQuestion = tokenizedOldQuestion.join(' ');
    },
    prepareSubSpanAttack(){
      var indices = this.$store.state.attackResults[0].adversarial.indices;
      var oldContext = this.$store.state.attackResults[0].predictions[0].prediction_documents[0].document;
      // tokenize the question by white space
      var tokenizedOldContext = oldContext.split(/\s+/);
      this.maxLenSpan = tokenizedOldContext.length;
      // for each elem in tokenizedOldContext, if it is not in indices, add <s>
      for (var i=0; i<tokenizedOldContext.length; i++){
        if (!indices.includes(i)){
          tokenizedOldContext[i] = '<s>'+tokenizedOldContext[i]+'</s>';
        } else {
          tokenizedOldContext[i] = '<mark class="bg-success text-white">'+tokenizedOldContext[i]+'</mark>';
        }
      }
      this.newContext = tokenizedOldContext.join(' ');
      this.newAnswer = this.$store.state.attackResults[0].predictions[1].prediction_output['output'];
      this.newQuestion = this.$store.state.attackResults[0].predictions[1].question;
    },
    prepareTopKAttack(){
      var indices = this.$store.state.attackResults[0].adversarial.indices;
      var oldContext = this.$store.state.attackResults[0].predictions[0].prediction_documents[0].document;
      // tokenize the question by white space
      var tokenizedOldContext = oldContext.split(/\s+/);
      this.maxTopK = tokenizedOldContext.length;
      // for each elem in tokenizedOldContext, if it is not in indices, add <s>
      for (var i=0; i<tokenizedOldContext.length; i++){
        if (!indices.includes(i)){
          tokenizedOldContext[i] = '<s>'+tokenizedOldContext[i]+'</s>';
        } else {
          tokenizedOldContext[i] = '<mark class="bg-success text-white">'+tokenizedOldContext[i]+'</mark>';
        }
      }
      this.newContext = tokenizedOldContext.join(' ');
      this.newAnswer = this.$store.state.attackResults[0].predictions[1].prediction_output['output'];
      this.newQuestion = this.$store.state.attackResults[0].predictions[1].question;
    },

    close(){
      // remove activate class from all buttons
      var btn_list = document.getElementsByClassName('btn-outline-secondary');
      for (var i = 0; i < btn_list.length; i++) {
        btn_list[i].classList.remove('active');
      }
      // reset modal
      this.numFlips = 1;
      this.lenSpan = 3;
      this.numTopK = 1;
      this.numReductions = 1;
      this.setAllButtonsUnselected();
      this.showAttackOutput = false;
      this.saliencyMethod = 'simple_grads';
      this.question = "";
      this.newContext = "";
      this.newAnswer = "";
      this.waiting = false;
    }
    
  },
})
</script>