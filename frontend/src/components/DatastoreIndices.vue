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
                <span
                  class="badge fs-6 ms-1 mb-1 float-end"
                  :style="{color: 'black'}"
                >
                  {{
                    selectDatastore.indices[row - 1]
                      ? selectDatastore.indices[row - 1].doc_encoder_model
                      : "-"
                  }}
                </span>
                <span
                  v-html="
                    selectDatastore.indices[row - 1]
                      ? selectDatastore.indices[row - 1].name
                      : '-'
                  "
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";

let my_value = [
  {
    skill: {
      name: "CommonsenseQA BERT Adapter",
      description:
        "A multiple-choice QA skill with bert-base-uncased as base model with the bert-base-uncased-pf-commonsense_qa adapter.",
    },
    predictions: [
      {
        prediction_score: 0.38965174555778503,
        prediction_output: {
          output: "waterfall",
        },
      },
    ],
    adversarial: null,
  },
  {
    skill: {
      name: "CommonsenseQA BERT Adapter",
      description:
        "A multiple-choice QA skill with bert-base-uncased as base model with the bert-base-uncased-pf-commonsense_qa adapter.",
    },
    predictions: [
      {
        prediction_score: 0.38965174555778503,
        prediction_output: {
          output: "waterfall",
        },
      },
    ],
    adversarial: null,
  },
  {
    skill: {
      name: "CommonsenseQA BERT Adapter",
      description:
        "A multiple-choice QA skill with bert-base-uncased as base model with the bert-base-uncased-pf-commonsense_qa adapter.",
    },
    predictions: [
      {
        prediction_score: 0.38965174555778503,
        prediction_output: {
          output: "waterfall",
        },
      },
    ],
    adversarial: null,
  },
];

export default Vue.component("datastore-indices", {
  props: {
    selectedDatastores: {
      type: Array,
      required: true,
      default: () => [],
    }
  },
  computed: {
    currentResults() {
      // return this.$store.state.currentResults
      return my_value;
    },
  },
});
</script>
