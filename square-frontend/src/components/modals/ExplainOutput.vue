<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
        </div>
        <div class="modal-body">
          <div class="text-center">
            <h3 class="card-title mb-3">Explain the output</h3>
          </div>
        </div>

   

        <div> 
          <h4>Method:</h4>

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



export default Vue.component("explain-output",{
  props:['test'],  //args should be the test json file
  mixins:[mixin], // ??
  components:{
    //BadgePopover // maybe useful
  },
  method:{
    // write functions here

  },
}
)


</script>

<style scoped>

</style>