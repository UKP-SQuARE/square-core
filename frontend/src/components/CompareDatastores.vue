<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container">
          <div class="row align-items-center mb-2 ">
            <div class="col col-sm-4">
              <div class="input-group input-group-sm mb-2">
                  <span class="input-group-text" id="basic-addon1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                      <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"></path>
                    </svg>
                  </span>
                <input v-model="searchText" placeholder="Search datastore" class="form-control form-control-xs"/>
              </div>
            </div> <!-- end search col -->
          </div>
        </div>
<!--        <p>{{this.getAllAvailablDatastores[0]["name"]}}</p>-->

        <div class="container text-center" style="height: 20em; overflow-y: scroll;">
          <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3" >
            <div class="col mb-2" v-for="(datastore, index) in filteredDatastore" :key="datastore.name">
              <div class="d-flex flex-wrap w-100 h-100">
                <input class="btn-check" type="checkbox"
                       :id="datastore.name"
                       v-on:input="selectDatastore(datastore.name)"
                >
                <label class="btn btn-outline-primary d-flex align-middle align-items-center justify-content-center w-100 h-100" :for="datastore.name"
                       data-bs-toggle="tooltip" data-bs-placement="top"  style="--bs-bg-opacity: 1">
                            <span class="text-break">{{index+1}}.{{datastore.name}},
<!--                            <br>-->
<!--                                                          <small class="text-muted">-->
<!--                                                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">-->
<!--                                                                <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>-->
<!--                                                                <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>-->
<!--                                                              </svg>-->
<!--                                                              {{datastore.fields}}-->
<!--                                                              <span class="px-1.5 text-gray-300">• </span>-->
<!--                                                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-seam" viewBox="0 0 16 16">-->
<!--                                                                <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>-->
<!--                                                              </svg>-->
<!--&lt;!&ndash;                                                              {{skillModelType(skill)}}&ndash;&gt;-->
<!--                                                            </small>-->
                            </span>
                </label>
              </div>


            </div>

          </div>
        </div>


      </div>
    </div>
  </div></template>

<script>


import Vue from 'vue'

export default Vue.component('compare-datastores',
{
  props: ['selectorTarget', 'skillFilter'],
  data() {
    return {
      searchText: '',
      waiting: false,
      options: {
        selectedDatastores: []
      },

      mock_datastores:[ { "name": "bioasq", "fields": [ { "name": "text", "type": "text" }, { "name": "title", "type": "text" } ] }, { "name": "conceptnet-kg", "fields": [ { "name": "description", "type": "text" }, { "name": "in_id", "type": "keyword" }, { "name": "name", "type": "keyword" }, { "name": "out_id", "type": "keyword" }, { "name": "type", "type": "keyword" }, { "name": "weight", "type": "double" } ] }, { "name": "msmarco", "fields": [ { "name": "text", "type": "text" }, { "name": "title", "type": "text" } ] }, { "name": "nq", "fields": [ { "name": "text", "type": "text" }, { "name": "title", "type": "text" } ] } ],
    }
  },
  computed:{
    filteredDatastore() {
      return this.searchText
          ? this.getAllAvailablDatastores.filter((item) => this.searchText
              .toLowerCase()
              .split(" ")
              .every(v => item.name.toLowerCase().includes(v)))
          :this.getAllAvailablDatastores
    },
    getAllAvailablDatastores()
    {

      // return this.$store.state.availableDatastores

      return this.mock_datastores
    },
    // getAllAvailablSkills()
    // {
    //   return this.$store.state.availableSkills
    //
    //
    // }
  },
  methods :{
    selectDatastore(datastore_name) {
      if(this.options.selectedDatastores.includes(datastore_name)){
        this.options.selectedDatastores.splice(this.options.selectedDatastores.indexOf(datastore_name),1)
        console.log('Delete '+datastore_name+' from selected datastore')
        // console.log(this.options.selectedDatastores)

      }
      else{
        this.options.selectedDatastores.push(datastore_name)
        console.log(datastore_name+' is added into selected datastore')
        // console.log(this.options.selectedDatastores)


      }
      this.$emit('input', this.options)

    }
  },
  mounted() {


  },
  beforeMount() {



    this.waiting = true

    this.$store.dispatch('updateDatastores').then(

    )
  }
})
</script>

<style scoped>

</style>