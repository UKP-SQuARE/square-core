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
                  <h1> Attack Mode </h1>
                  <hr/>
              </div>
            </div>

            <div class="row">
              <div class="col-2 text-start">
                  <h4>Method:</h4>
              </div>
              <div class="col-5">
                  <button v-on:click="methodSelected('HotFlip')" type="button" class="btn btn-outline-warning">HotFlip</button>
              </div>
              <div class="col-5">
                  <button v-on:click="methodSelected('Input_Red')" type="button" class="btn btn-outline-warning">Input Reduction</button>
              </div>
            </div>

            <!-- <div class="row mt-3">
              <div class="col-auto text-start">
                  <h4>Gradient Method:</h4>
              </div>
              <div class="col-auto">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SimpleGrad" value="SimpleGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="SimpleGrad">Simple Gradients</label>
                </div>
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="SmoothGrad" value="SmoothGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="SmoothGrad">Simple Gradients</label>
                </div>
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" id="IntegratedGrad" value="IntegratedGrad" v-model="gradient_way"/>
                  <label class="form-check-label" for="IntegratedGrad">IntegratedGrad</label>
                </div>  
              </div>
            </div> -->

            <div v-if="hotflip_selected" class="row mt-3">
                <div class="col-auto text-start">
                    <h4>Parameters:</h4>
                </div>
                <div class="col-auto">
                    <div class="form-floating">
                    <select class="form-select" id="gradientWay" v-model="gradient_way">
                        <option value="SimpleGrad">Simple Gradients</option>
                        <option value="SmoothGrad">Smooth Gradients</option>
                        <option value="IntegratedGrad">Integrated Gradients</option>
                    </select>
                    <label for="gradientWay">Gradient Method..</label>
                    </div>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <label class="form-check-label" for="includeAns">Include Answer</label>
                        <input class="form-check-input" type="checkbox" id="includeAns">
                    </div>
                </div>

                <div class="col-auto">
                    <div class="form-check form-switch">
                        <label class="form-check-label" for="includeAns"># of flips:</label>
                        <input type="range" min="0" :max="10" v-model="numFlips" class="form-range" id="numFlips" >
                        <output ></output>
                    </div>
                </div>
            </div>

            <div v-if="hotflip_selected" class="row mt-3">
                <div class="col-12">
                    <button v-on:click="attack('HotFlip')" type="button" class="btn btn-outline-warning">Attack Skill!</button>
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
// import hotflip from './hotflip_squad_v1.json'
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
      inputred_selected: false
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
    
  },
})
</script>