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
            </div> <!-- row -->

            <div class="row">
              <div class="col-4 text-start">
                  <h4>Method:</h4>
              </div>
              <div class="col btn-group flex-wrap" role="group" aria-label="Basic example">
                <button id="hotflip_btn" v-on:click="attack('hotflip')" type="button" class="btn btn-outline-primary" :disabled="waiting_hotflip">
                  <span v-show="waiting_hotflip" class="spinner-border spinner-border-sm" role="status"/>&nbsp;HotFlip
                </button>
                <button id="input_reduction_btn" v-on:click="attack('input_reduction')" type="button" class="btn btn-outline-primary" :disabled="waiting_input_reduction">
                  <span v-show="waiting_input_reduction" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Input Reduction
                </button>
                <button id="sub_span_btn" v-on:click="attack('sub_span')" type="button" class="btn btn-outline-primary" :disabled="waiting_sub_span">
                  <span v-show="waiting_sub_span" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Sub-Span
                </button>
                <button id="topk_tokens_btn" v-on:click="attack('topk_tokens')" type="button" class="btn btn-outline-primary" :disabled="waiting_topk_tokens">
                  <span v-show="waiting_topk_tokens" class="spinner-border spinner-border-sm" role="status"/>&nbsp;Top K
                </button>
              </div>
              
            </div> <!-- row -->
            
            <div v-if="method == 'hotflip' || method == 'sub_span' || method == 'topk_tokens'" class="row mt-3">
              <div class="col-4 text-start">
                  <h4>Saliency Method:</h4>
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SimpleGrad" value="simple_grads" v-model="saliencyMethod" v-on:click="attack('')"/>
                  <label class="form-check-label" for="SimpleGrad">Simple Gradients</label>
                </div>
              </div>

              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SmoothGrad" value="smooth_grads" v-model="saliencyMethod" v-on:click="attack('')"/>
                  <label class="form-check-label" for="SmoothGrad">Smooth Gradients</label>
                </div>
              </div>

              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="IntegratedGrad" value="integrated_grads" v-model="saliencyMethod" v-on:click="attack('')"/>
                  <label class="form-check-label" for="IntegratedGrad">IntegratedGrad</label>
                </div>  
              </div>

              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="attention" value="attention" v-model="saliencyMethod" v-on:click="attack('')"/>
                  <label class="form-check-label" for="attention">Attention</label>
                </div>  
              </div>

            </div> <!-- row -->

            <div v-if="method == 'hotflip'" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># Flips = {{numFlips}}</h4>
                </div>
                <div class="col-8 text-start">
                  <div class="form-check-inline">
                    <input type="range" min="1" :max="maxFlips" v-model="numFlips" class="form-range" id="numFlips" @click="showAttack()"/>
                  </div>
                </div>  
                
            </div>

            <div v-if="method == 'input_reduction'" class="row mt-3">
                <div class="col-4 text-start">
                  <h4># Reductions = {{numReductions}}</h4>
                </div>
                <div class="col-auto">
                  <div class="form-check-inline">
                    <input type="range" min="1" :max="maxReductions" v-model="numReductions" class="form-range" id="numReductions" @click="showAttack()">
                  </div>
                </div>
            </div>

            <div v-if="method == 'sub_span'" class="row mt-3">
                <div class="col-4 text-start">
                    <h4>Length of sub-span = {{lenSpan}}</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check-inline">
                        <input type="range" min="2" :max="maxLenSpan" v-model="lenSpan" v-on:click="attack('')" class="form-range" id="lenSpan">
                    </div>
                </div>
            </div>

            <div v-if="method == 'topk_tokens'" class="row mt-3">
                <div class="col-4 text-start">
                    <h4>Top k = {{numTopK}}</h4>
                </div>

                <div class="col-auto">
                    <div class="form-check-inline">
                        <input type="range" min="1" :max="maxTopK" v-model="numTopK" v-on:click="attack('')" class="form-range" id="numTopK">
                    </div>
                </div>
            </div>

            <div v-if="showAttackOutput">
              <div class="row mt-3" v-for="(skillResult, index) in this.$store.state.attackResults" :key="index">
                <div class="col-12">
                  <h4>{{ skillResult.skill.name }}</h4>
                  <hr/>
                </div>

                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Question:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="listNewQuestion[index]"/>
                    </div>
                  </div>

                  <div class="row mt-3">
                    <div class="col-2 text-start">
                      <h4>Context:</h4>
                    </div>
                    <div class="col-10">
                      <span v-html="listNewContext[index]"/>
                    </div>
                  </div>

                  <div class="row mt-3 align-items-center">
                      <div class="col-4 text-start">
                        <h4>New Answer:</h4>
                      </div>
                      <div class="col-3 text-start vertical-center">
                          <span v-html="listNewAnswer[index]"/>
                      </div>
                      <div class="col-2 text-start ">
                          <h4>Old Answer:</h4>
                      </div>
                      <div class="col-3 text-start">
                          {{$store.state.currentResults[index].predictions[0]['prediction_output']['output']}}
                      </div>
                  </div> <!-- end newAnswer -->

              </div> <!-- end for loop -->
            </div> <!-- end show saliency map -->
            
            
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
      // form data
      method: undefined,
      saliencyMethod: 'simple_grads',
      numFlips: 1,
      maxFlips: 8, //this.$store.state.currentContext.split(/\s+/).length,
      lenSpan: 3,
      maxLenSpan: this.$store.state.currentContext.split(/\s+/).length,
      numTopK: 1,
      maxTopK: this.$store.state.currentContext.split(/\s+/).length,
      numReductions: 1,
      maxReductions: this.$store.state.currentQuestion.split(' ').length,
      // output data
      listNewQuestion: [],
      listNewContext: [],
      listNewAnswer: [],
      // waiting flags
      waiting_hotflip: false,
      waiting_input_reduction: false,
      waiting_sub_span: false,
      waiting_topk_tokens: false,
      // other flags
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
    methodSelected(){
      this.showAttackBtn = true;
      this.hideOutput();
      if(this.method == 'input_reduction'){
        this.saliencyMethod = 'attention';
      }
    },
    setCallingBtnActive(method){
      if (method !== ''){
        document.getElementById(method+"_btn").classList.add("active");
      }      
    },
    setAllBtnInactive(){
      document.getElementById("hotflip_btn").classList.remove("active");
      document.getElementById("input_reduction_btn").classList.remove("active");
      document.getElementById("sub_span_btn").classList.remove("active");
      document.getElementById("topk_tokens_btn").classList.remove("active");
    },
    hideOutput(){
      this.showAttackOutput = false;
      this.newAnswer = "";
    },
    attack(method) {
      if (method !== ''){
        this.method = method;
      }
      // restarting interface
      this.setAllBtnInactive();
      this.showAttackOutput = false;
      // starting procedure
      this.runSpinners();
      /* eslint-disable */
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
        this.showAttackOutput = true;
        this.showAttack();
        this.setCallingBtnActive(this.method);
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        this.stopSpinners();
      })
    },
    prepareAttackKwargs(){
      var attack_kwargs = {method: this.method, saliency_method: this.saliencyMethod,}
      // if method is hotflip, add max_flips
      if(this.method == 'hotflip'){
        attack_kwargs['max_flips'] = parseInt(this.maxFlips);
      }
      // if method is input_reduction, add max_reductions
      if(this.method == 'input_reduction'){
        // tokenize currentQuestion
        attack_kwargs['max_reductions'] = parseInt(this.maxReductions);
        attack_kwargs['saliency_method'] = 'attention';
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
      var listQAPairs = [];
      if (this.method == 'hotflip'){
        for (var i=0; i<this.$store.state.attackResults.length; i++){
          var qaPair = this.processHotFlipAttack(this.$store.state.attackResults[i]);
          listQAPairs.push(qaPair);
        }
      } else if (this.method == 'input_reduction'){
        for (var i=0; i<this.$store.state.attackResults.length; i++){
          var qaPair = this.processInputReductionAttack(this.$store.state.attackResults[i]);
          listQAPairs.push(qaPair);
        }
      } else if (this.method == 'sub_span'){
        for (var i=0; i<this.$store.state.attackResults.length; i++){
          var qaPair = this.processSubSpanAttack(this.$store.state.attackResults[i]);
          listQAPairs.push(qaPair);
        }
      } else if (this.method == 'topk_tokens'){
        for (var i=0; i<this.$store.state.attackResults.length; i++){
          var qaPair = this.processTopKAttack(this.$store.state.attackResults[i]);
          listQAPairs.push(qaPair);
        }
      }
      this.listNewQuestion = listQAPairs.map(qaPair => qaPair.newQuestion);
      this.listNewContext = listQAPairs.map(qaPair => qaPair.newContext);
      this.listNewAnswer = listQAPairs.map(qaPair => qaPair.newAnswer);
    },
    processHotFlipAttack(attackResult){
      var indices = attackResult.adversarial.indices;
      var context = attackResult.predictions[0].prediction_documents[0].document;
      var listContexts = []
      for (var i = 1; i < attackResult.predictions.length; i++) {
        var prediction = attackResult.predictions[i];
        listContexts.push(prediction.prediction_documents[0].document);
      }
      // tokenize the context by white space
      var tokenizedContext = context.split(/\s+/);
      // this.maxFlips = tokenizedContext.length;
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
      var newContext = tokenizedContext.join(' ');
      var newAnswer = attackResult.predictions[this.numFlips].prediction_output['output'];
      var newQuestion = attackResult.predictions[this.numFlips].question;
      return {newQuestion, newContext, newAnswer};
    },
    processInputReductionAttack(attackResult){
      var indices = attackResult.adversarial.indices;
      var oldQuestion = attackResult.predictions[0].question;
      // tokenize the question by white space
      var tokenizedOldQuestion = oldQuestion.split(/\s+/);
      this.maxReductions = tokenizedOldQuestion.length;
      // flip context token with indices
      for (var redIdx=0; redIdx<this.numReductions; redIdx++){
        var oldToken = tokenizedOldQuestion[indices[redIdx]];
        
        var highLightedToken = '<s><mark class="bg-danger text-white">'+oldToken+'</mark></s>'
        tokenizedOldQuestion[indices[redIdx]] = highLightedToken
      }
      var newContext = attackResult.predictions[this.numReductions].prediction_documents[0].document;
      var newAnswer = attackResult.predictions[this.numReductions].prediction_output['output'];
      var newQuestion = tokenizedOldQuestion.join(' ');
      return {newQuestion, newContext, newAnswer};
    },
    processSubSpanAttack(attackResult){
      var indices = attackResult.adversarial.indices;
      var oldContext = attackResult.predictions[0].prediction_documents[0].document;
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
      var newContext = tokenizedOldContext.join(' ');
      var newAnswer = attackResult.predictions[1].prediction_output['output'];
      var newQuestion = attackResult.predictions[1].question;
      return {newQuestion, newContext, newAnswer};
    },
    processTopKAttack(attackResult){
      var indices = attackResult.adversarial.indices;
      var oldContext = attackResult.predictions[0].prediction_documents[0].document;
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
      var newContext = tokenizedOldContext.join(' ');
      var newAnswer = attackResult.predictions[this.numTopK].prediction_output['output'];
      var newQuestion = attackResult.predictions[this.numTopK].question;
      return {newQuestion, newContext, newAnswer};
    },
    runSpinners(){
      this.setSpinners(true);
    },
    stopSpinners(){
      this.setSpinners(false);
    },
    setSpinners(value){
      switch(this.method){
        case 'hotflip':
          this.waiting_hotflip = value;
          break;
        case 'input_reduction':
          this.waiting_input_reduction = value;
          break;
        case 'sub_span':
          this.waiting_sub_span = value;
          break;
        case 'topk_tokens':
          this.waiting_topk_tokens = value;
          break;
      }
    },   
    close(){
      // remove activate class from all buttons
      this.setAllBtnInactive();
      // reset modal
      this.numFlips = 1;
      this.lenSpan = 3;
      this.numTopK = 1;
      this.numReductions = 1;
      this.showAttackOutput = false;
      this.saliencyMethod = 'simple_grads';
      this.question = "";
      this.newContext = "";
      this.newAnswer = "";
      this.stopSpinners();
    }
    
  },
})
</script>