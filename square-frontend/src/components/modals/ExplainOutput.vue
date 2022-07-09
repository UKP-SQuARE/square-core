<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
        </div>
        <div class="modal-body">
          <!-- <div class="text-center">
            <h3 class="card-title mb-3">Explain the output</h3>
          </div> -->
        </div>

   
        <!-- <div>
           <h3>{{test}}</h3> 
        </div> -->
        <div class="row"> 
          <h4 class="col-sm-2">Method:
         
          </h4>
            
            <button v-on:click="greet" type="button" class="btn btn-default col-sm-2">Attention</button>
            <button type="button" class="btn btn-default col-sm-2">Scaled Attention</button>
            <button type="button" class="btn btn-default col-sm-2">Simple Grad</button>
            <button type="button" class="btn btn-default col-sm-2">Smooth Grad</button>
            <button type="button" class="btn btn-default col-sm-2">Integrated Grad</button>



        </div>
          

        <div> 
          <h4>Question:</h4>

        </div>

        <div> 
          <h4>Context:</h4>

        </div>

      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
//import BadgePopover from '../BadgePopover'
import mixin from '@/components/results/mixin.vue'
import { postQuery } from '../../api'



export default Vue.component("explain-output",{
  // data () { return {
  //   count: 0
  // }},
  props:['test'],  //args should be the test json file
  mixins:[mixin], // ??
  components:{
    //BadgePopover // maybe useful
  },
  methods:{
    // write functions here
    postReq() {

      postQuery()
    },
    greet: function() {
      alert(this.$store)    }
  },
}
)


</script>

<style scoped>

</style>