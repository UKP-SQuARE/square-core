<template>
  <div class="bg-light border rounded shadow h-100 p-3">
    <div class="w-100">
      <div class="mb-3">
        <div class="container">
          <div class="row align-items-center mb-2">
            <div class="col col-sm-4">
              <div class="input-group input-group-sm mb-2">
                <span class="input-group-text" id="basic-addon1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    class="bi bi-search"
                    viewBox="0 0 16 16"
                  >
                    <path
                      d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"
                    ></path>
                  </svg>
                </span>
                <input
                  v-model="searchText"
                  placeholder="Search datastore"
                  class="form-control form-control-xs"
                />
              </div>
            </div>
          </div>
        </div>
        <div
          class="container text-center"
          style="height: 20em; overflow-y: scroll"
        >
          <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3">
            <div
              class="col mb-2"
              v-for="(datastore, index) in filteredDatastore"
              :key="datastore.name"
            >
              <div class="d-flex flex-wrap w-100 h-100">
                <input
                  class="btn-check"
                  type="checkbox"
                  :id="datastore.name"
                  v-on:input="selectDatastore(datastore.name)"
                />
                <label
                  class="btn btn-outline-primary d-flex align-middle align-items-center justify-content-center w-100 h-100"
                  :for="datastore.name"
                  data-bs-toggle="tooltip"
                  data-bs-placement="top"
                  style="--bs-bg-opacity: 1"
                >
                  <span class="text-break"
                    >{{ index + 1 }}. {{ datastore.name }}
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
  props: ["selectorTarget", "skillFilter"],
  data() {
    return {
      searchText: "",
      waiting: false,
      options: {
        selectedDatastores: [],
      },

      mock_datastores: [
        {
          name: "bioasq",
          fields: [
            { name: "text", type: "text" },
            { name: "title", type: "text" },
          ],
          indices: [
            {
              datastore_name: "bioasq",
              name: "distilbert",
              doc_encoder_model: "msmarco-distilbert-base-tas-b",
              doc_encoder_adapter: null,
              query_encoder_model:
                "sentence-transformers/msmarco-distilbert-base-tas-b",
              query_encoder_adapter: null,
              embedding_size: 768,
              embedding_mode: "cls",
              index_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/bioasq-distilbert-base-tas-b.size-full/bioasq-QT_8bit_uniform-ivf262144.index",
              index_ids_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/bioasq-distilbert-base-tas-b.size-full/bioasq-QT_8bit_uniform-ivf262144.txt",
              index_description: "QT_8bit-IVF65536",
              collection_url: "http://www.bioasq.org/",
            },
          ],
        },
        {
          name: "conceptnet-kg",
          fields: [
            { name: "description", type: "text" },
            { name: "in_id", type: "keyword" },
            { name: "name", type: "keyword" },
            { name: "out_id", type: "keyword" },
            { name: "type", type: "keyword" },
            { name: "weight", type: "double" },
          ],
          indices: [],
        },
        {
          name: "msmarco",
          fields: [
            { name: "text", type: "text" },
            { name: "title", type: "text" },
          ],
          indices: [
            {
              datastore_name: "msmarco",
              name: "distilbert",
              doc_encoder_model: "msmarco-distilbert-base-tas-b",
              doc_encoder_adapter: null,
              query_encoder_model:
                "sentence-transformers/msmarco-distilbert-base-tas-b",
              query_encoder_adapter: null,
              embedding_size: 768,
              embedding_mode: "cls",
              index_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/msmarco-distilbert-base-tas-b.size-full/msmarco-QT_8bit_uniform-ivf65536.index",
              index_ids_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/msmarco-distilbert-base-tas-b.size-full/msmarco-QT_8bit_uniform-ivf65536.txt",
              index_description: "QT_8bit-IVF65536",
              collection_url:
                "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/msmarco.zip",
            },
          ],
        },
        {
          name: "nq",
          fields: [
            { name: "text", type: "text" },
            { name: "title", type: "text" },
          ],
          indices: [
            {
              datastore_name: "nq",
              name: "dpr",
              doc_encoder_model: "facebook/dpr-ctx_encoder-single-nq-base",
              doc_encoder_adapter: null,
              query_encoder_model:
                "facebook/dpr-question_encoder-single-nq-base",
              query_encoder_adapter: null,
              embedding_size: 768,
              embedding_mode: "pooler",
              index_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.index",
              index_ids_url:
                "https://public.ukp.informatik.tu-darmstadt.de/kwang/faiss-instant/dpr-single-nq-base.size-full/nq-QT_8bit_uniform-ivf262144.txt",
              index_description:
                "It uses Faiss-IVF-SQ with nlist = 2^18, nprobe = 512 and 8bit uniform. For the indexing script, please refer to https://gist.github.com/kwang2049/d23550604059ed1576ac6cffb7e09fb2",
              collection_url:
                "https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz",
            },
          ],
        },
      ],
    };
  },
  computed: {
    filteredDatastore() {
      return this.getAllAvailablDatastores.filter((datastore) => {
        return datastore.name.toLowerCase().includes(this.searchText.toLowerCase());
      });
    },
    getAllAvailablDatastores() {
      return this.mock_datastores;
    },
  },
  methods: {
    selectDatastore(datastore_name) {
      let index = this.options.selectedDatastores.findIndex(obj => obj.name === datastore_name);
      console.log(index);
      if(index !== -1){
        this.options.selectedDatastores.splice(index, 1);
        console.log("Delete " + datastore_name + " from selected datastore");
      }else{
        this.options.selectedDatastores.push(this.getAllAvailablDatastores.find(obj => obj.name === datastore_name));
        console.log(datastore_name + " is added into selected datastore");
      }
      this.$emit("input", this.options);
    },
  },
  beforeMount() {
    this.waiting = true;
    this.$store.dispatch("updateDatastores").then();
  },
});
</script>
