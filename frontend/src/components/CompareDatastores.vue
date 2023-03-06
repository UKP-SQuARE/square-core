<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container">
          <div class="row align-items-center mb-2">
            <div class="col col-sm-4">
              <div class="input-group input-group-sm mb-2">
                <span class="input-group-text" id="basic-addon1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search"
                    viewBox="0 0 16 16">
                    <path
                      d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z">
                    </path>
                  </svg>
                </span>
                <input v-model="searchText" placeholder="Search datastore" class="form-control form-control-xs" />
              </div>
            </div>
          </div>
        </div>
        <div class="container text-center" style="height: 20em; overflow-y: scroll">
          <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3">
            <div class="col mb-2" v-for="(datastore, index) in filteredDatastore" :key="datastore.name">
              <div class="d-flex flex-wrap w-100 h-100">
                <input class="btn-check" type="checkbox" :id="datastore.name"
                  v-on:input="selectDatastore(datastore.name)" />
                <label
                  class="btn btn-outline-primary d-flex align-middle align-items-center justify-content-center w-100 h-100"
                  :for="datastore.name" data-bs-toggle="tooltip" data-bs-placement="top" style="--bs-bg-opacity: 1">
                  <span class="text-break">{{ index + 1 }}. {{ datastore.name }}
                  </span>
                </label>

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import Vue from "vue";

export default Vue.component("compare-datastores", {
  props: ["selectorTarget",],
  data() {
    return {
      searchText: "",
      waiting: false,
      options: {
        selectedDatastores: [],
      },
    };
  },
  computed: {
    filteredDatastore() {
      return this.getAllAvailablDatastores.filter((datastore) => {
        return datastore.name.toLowerCase().includes(this.searchText.toLowerCase());
      });
    },
    getAllAvailablDatastores() {
      console.log(this.$store.state.availableDatastores)
      return this.$store.state.availableDatastores
    },
    getAllAvailableIndices() {
      return this.$store.state.availableIndices;
    },
  },

  methods: {
    selectDatastore(datastore_name) {
      let index = this.options.selectedDatastores.findIndex(obj => obj.name === datastore_name);
      console.log(index);
      if (index !== -1) {
        this.options.selectedDatastores.splice(index, 1);
        console.log("Delete " + datastore_name + " from selected datastore");
      } else {
        this.options.selectedDatastores.push(this.getAllAvailablDatastores.find(obj => obj.name === datastore_name));
        console.log(datastore_name + " is added into selected datastore");
      }
      this.$emit("input", this.options);
    },
  },
  mounted() {

  },
  beforeMount() {
    this.waiting = true;
    this.$store.dispatch("updateDatastores").then(
      () => { this.$store.dispatch("updateIndices") }).then(
        console.log("before mount finish")
      );
  },
});
</script>
