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
              <div class="col-2 text-start">
                  <h4>Method:</h4>
              </div>
              <div class="col-5">
                  <button v-on:click="methodSelected('HotFlip')" type="button" class="btn btn-outline-primary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Flips words in the input to change the Skill's prediction.">
                    HotFlip
                  </button>
              </div>
              <div class="col-5">
                  <button v-on:click="methodSelected('Input_Red')" type="button" class="btn btn-outline-primary"
                   data-bs-toggle="tooltip" data-bs-placement="top" title="Removes as many words from the input as possible without changing the Skill's prediction.">
                    Input Reduction
                  </button>
                  
              </div>
            </div>

            <div v-if="hotflip_selected || inputred_selected" class="row mt-3">
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

            <div v-if="hotflip_selected || inputred_selected" class="row mt-3">
                <div class="col-4 text-start">
                    <h4># flips:</h4>
                </div>

                <div class="col-6">
                    <div class="form-check form-switch">
                        <input type="range" min="0" max="20" v-model="numFlips" class="form-range" id="numFlips" oninput="this.nextElementSibling.value = this.value">
                        <output ></output>
                    </div>
                </div>

                <div v-if="hotflip_selected" class="col-2">
                    <div class="form-check form-switch">
                        <label class="form-check-label" for="includeAns">Include Answer</label>
                        <input class="form-check-input" type="checkbox" id="includeAns">
                    </div>
                </div>
            </div>

            <div v-if="hotflip_selected" class="row mt-3">
              <div class="col-12">
                  <button v-on:click="attack('HotFlip')" type="button" class="btn btn-outline-primary">Attack Skill!</button>
              </div>
            </div>

            <div v-if="inputred_selected" class="row mt-3">
              <div class="col-12">
                    <button v-on:click="attack('Input_Red')" type="button" class="btn btn-outline-warning">Attack Skill!</button>
                </div>
            </div>

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
                  <h4>Flipped Context:</h4>
              </div>
              <div class="col-8 text-start">
                  <span v-html="showFlipContext()"/>
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
import hotflip from './hotflip.json'
// import input_red from './input_reduction_squad.json'
export default Vue.component("attack-output",{
  data () {
     return {
      num_Maxshow : this.num_Maxshow ,
      num_show : this.num_show ,
      gradient_way: 'SimpleGrad',
      includeAns: false,
      numFlips: 0,
      hotflip_selected: false,
      inputred_selected: false,
      question: '',
      flippedContext: "",
      newAnswer: "",
      hotflipWaiting: false,
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
      if(method == 'HotFlip'){
        this.hotflip_selected = true;
        this.inputred_selected = false;
      }
      else{
        this.hotflip_selected = false;
        this.inputred_selected = true;
      }
    },
    attack(method) {
      if(method == 'HotFlip'){
        // make the call to the api
        this.hotflipWaiting = true;

        // var listQuestionTokens = hotflip['question'].split(/\s+|\.|\!|\?|\;/);
        /* eslint-disable */
        var listContextTokens = hotflip['context'].split(/\s+|\.|\!|\?|\;/);
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
        this.flippedContext = listContextTokens.join(' ');
        this.question = hotflip['question'];
        this.newAnswer = hotflip['new_answer'];
        this.showHotFlipOutput = true;
      }
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
        // this.failure = false,
        // this.num_Maxshow =  request_json['explain_kwargs']['top_k']
        // this.num_show = request_json['explain_kwargs']['top_k']
        // console.log("Query successed! "),
        // this.$store.state.currentQuestion = request_json['input'][0][0]
        // this.$store.state.currentContext = request_json['input'][0][1]
        // this.response = context_json //get the response from local json
     
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        this.waiting = false
      })
    },
    showFlipContext(){
      return this.flippedContext;
    },
    
  },
})
</script>