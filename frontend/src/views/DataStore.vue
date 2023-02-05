<template>
  <div>
    <form>
      <div class="row mt-4 mt-md-0 mb-4">
        <div class="accordion" id="accordionExample">
          <div class="accordion-item">
            <h2 class="accordion-header" id="headingOne">
              <button
                id="btn_collapseOne"
                class="accordion-button"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#collapseOne"
                aria-expanded="true"
                aria-controls="collapseOne"
              >
                Selected Datastores: {{ strSelectedDatastores }}
              </button>
            </h2>
            <div
              id="collapseOne"
              class="accordion-collapse collapse show"
              aria-labelledby="headingOne"
              data-bs-parent="#accordionExample"
            >
              <div class="accordion-body">
                <CompareDatastores
                  v-on:input="changeSelectedDatastores"
                  class=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </form>
    <DatastoreIndices
      v-if="selectedDatastores.length > 0"
      v-bind:selectedDatastores="selectedDatastores"
    />
  </div>
</template>

<script>
import Vue from "vue";
import CompareDatastores from "@/components/CompareDatastores";
import DatastoreIndices from "@/components/DatastoreIndices";

export default Vue.component("data-store", {
  data() {
    return {
      test: 1,
      options: {
        selectedDatastores: [],
      },
    };
  },
  components: {
    CompareDatastores,
    DatastoreIndices,
  },
  computed: {
    selectedDatastores() {
      return this.options.selectedDatastores;
    },
    strSelectedDatastores() {
      console.log("str");
      return this.options.selectedDatastores.map(
        (datastore) => datastore.name
      ).join(", ");
    },
  },
  methods: {
    changeSelectedDatastores(options) {
      this.options = options;
      console.log("selected datastores changed");
      console.log(this.selectedDatastores);
    },
  },
});
</script>

<style scoped></style>
