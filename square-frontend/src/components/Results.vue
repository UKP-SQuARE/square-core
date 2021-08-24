<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <b-container>
    <hr />
    <b-tabs>
      <b-tab
        v-for="skillResult in currentResults"
        v-bind:key="skillResult.name"
      >
        <template v-slot:title>
        {{skillResult.name}} <small>{{parseInt(skillResult.meta_qa_score*100)}}% relevant</small>
        </template>
        <h6 class="text-muted mt-2 mb-1 ml-1">{{skillResult.description}}</h6>
        <b-card class="mt-2" v-show="skillResult.error">
          <b-card-text>Error: {{ skillResult.error }}</b-card-text>
        </b-card>
        <b-card
          v-for="res in skillResult.results"
          v-bind:key="res.prediction_id"
          class="mt-2"
          header-bg-variant="primary" 
          header-text-variant="white"
          footer-tag="footer"
        >
        <template #header>
          <h6 class="mb-0">
            <span style="float: left">{{res.prediction_output.output}}</span>
            <span style="float: right">{{res.prediction_output.output_score}}</span>
          </h6> 
        </template>
        <b-card-text v-html="highlight(res.prediction_documents[0].document, res.prediction_documents[0].span)"></b-card-text>
          <component :is="res.type" v-bind:result="res"></component>
        <template #footer>
        <div>
        <b-button
          v-b-toggle.collapse-2 class="mt-1">
          See similar documents ({{res.prediction_documents.length - 1}})
        </b-button>
        <b-collapse id="collapse-2" class="mt-2">
            <b-card>I should start open!</b-card>
          </b-collapse>
        </div>
      </template>
        </b-card>
      </b-tab>
    </b-tabs>
  </b-container>
</template>

<script>
import PlainText from "@/components/result/PlainText.vue";
import KeyValue from "@/components/result/KeyValue.vue";
import RawHTML from "@/components/result/HTML.vue";
export default {
  name: "results",
  components: {
    // Be careful that the name does not overlap with an existing HTML component (e.g. text, html)
    plain_text: PlainText,
    key_value: KeyValue,
    raw_html: RawHTML
  },
  computed: {
    currentQuestion() {
      return this.$store.state.currentQuestion;
    },
    currentResults() {
      return this.$store.state.currentResults.slice(0).sort((a,b) => {
        if (a["score"] < b["score"]) {
          return 1
        } else if(a["score"] === b["score"]) {
          return 0
        } else if(a["score"] > b["score"]) {
          return -1
        }
      });
    }
  },
  methods: {
    highlight(text, span) {
      return text.substring(0, span[0]) + '<span class="highlightText">' + text.substring(span[0], span[1]) + '</span>' + text.substring(span[1], text.length);
    }
  }
};
</script>
