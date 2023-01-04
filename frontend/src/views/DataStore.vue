<template>
  <form >
    <div class="row mt-4 mt-md-0 mb-4">
      <div class="accordion" id="accordionExample">
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingOne">
            <button  id="btn_collapseOne" class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
              Selected Datastores: {{strSelectedDatastores}}
            </button>
          </h2>
          <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
            <div class="accordion-body">
              <CompareDatastores v-on:input="changeSelectedDatastores" class="" />
<!--              <CompareSkills selector-target="qa" v-on:input="changeSelectedSkills" class="" />-->
            </div>
          </div>
        </div>

      </div>
    </div>
  </form>


</template>

<script>
import Vue from 'vue'
import CompareDatastores from '../components/CompareDatastores'


export default Vue.component('data-store',{
  data(){
    return {
      test:1,
      options: {
        selectedDatastores: []
      }
    }
  },
  components:{
    CompareDatastores
  },
  computed:{
    selectedDatastores() {
      return this.options.selectedDatastores
    },
    strSelectedDatastores() {
      // let availableDatastores = this.$store.state.availableDatastores;
      // availableDatastores = availableDatastores.filter(datastore => this.selectedDatastores.includes(datastore.name));
      console.log("str")

      return this.options.selectedDatastores.join(', ');
    },

  },
  methods: {
    changeSelectedDatastores(options) {
      this.options = options
      console.log("selected datastores changed")
      console.log(this.selectedDatastores)

    },
  }
    }
)

</script>

<style scoped>

</style>