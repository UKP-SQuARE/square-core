<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <b-container>
    <hr />
    <b-tabs>
      <b-tab
        v-for="skillResult in currentResults"
        v-bind:key="skillResult.name"
        v-bind:title="skillResult.name"
      >
        <h6 class="text-muted mt-2 mb-1 ml-1">{{skillResult.skill_description}}</h6>
        <b-card class="mt-2" v-show="skillResult.error">
          <b-card-text>Error: {{ skillResult.error }}</b-card-text>
        </b-card>
        <b-card
          v-for="(res, i) in skillResult.results"
          v-bind:key="skillResult.name+i"
          class="mt-2"
        >
          <component :is="res.type" v-bind:result="res"></component>
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
  }
};
</script>
