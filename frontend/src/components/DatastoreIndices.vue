<template>
  <div v-if="selectedDatastores.length">
    <div class="row">
      <div
        class="col table-responsive bg-light border border-primary rounded shadow p-3 mx-3 mt-4"
      >
        <table class="table table-borderless">
          <thead class="border-bottom border-dark">
            <tr>
              <th scope="col" />
              <th
                v-for="(selectDatastore, index) in selectedDatastores"
                :key="index"
                scope="col"
                class="fs-2 fw-light text-center"
              >
                {{ selectDatastore.name }}
              </th>
            </tr>
            <tr>
              <!-- <th scope="col" />
              <th
                v-for="(selectDatastore, index) in selectedDatastores"
                :key="index"
                scope="col"
                class="fw-normal text-center"
              >
                {{ selectDatastore.description }}
              </th> -->
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in Math.max(...selectedDatastores.map(datastore => datastore.indices.length))" :key="row">
              <th scope="row" class="pt-4 text-primary text-end">{{ row }}.</th>
              <td
                v-for="(selectDatastore, index) in selectedDatastores"
                :key="index"
                :width="`${100 / selectedDatastores.length}%`"
                style="min-width: 320px"
                class="pt-4"
                v-bind:style="{ 'border-left': '1px solid #ddd' }"
              >

                <div  v-if="selectDatastore.indices[row - 1]!=Null" >
                  <table
                      v-for=" (val,key,index) in  selectDatastore.indices[row - 1]"
                      :key="key"
                      >

<!--                                      <p>{{ typeof(selectDatastore.indices[row - 1])}}</p>-->


                    <tr v-if="index <=2|| showAllIndices">
                      <th scope="row" style="vertical-align: top;">{{key}}:</th>
                      <td >{{val}}</td>
                    </tr>

                  </table>
                </div>

              </td>
            </tr>
          </tbody>
        </table>

      </div>
    </div>
    <div class="d-grid gap-1 d-md-flex justify-content-md-center">
      <button v-on:click="changeShowAllIndices()"  class="btn btn-danger btn-lg shadow text-white" id="btn-showAll" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
         <span v-if="!showAllIndices">Show Details</span>
        <span v-if="showAllIndices">Hide Details</span>
      </button>
    </div>

  </div>

</template>

<script>
import Vue from "vue";



export default Vue.component("datastore-indices", {
  props: {
    selectedDatastores: {
      type: Array,
      required: true,
      default: () => [],
    }
  },
  data() {
    return {
      showAllIndices:false
    }

  },
  computed: {

  },
  methods:{
    changeShowAllIndices(){
      this.showAllIndices = !this.showAllIndices
      console.log(this.showAllIndices)
    }
  }
});
</script>
