<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
  <td class="pt-4">
    <div class="container">
      <div class="row">
        <div class="col col-8 text-start">
          <span v-html="output" />
        </div>
        <div class="col text-end">
          <span class="badge fs-6 ms-1 mb-1"
            :style="{ 'background-color': colorFromGradient(prediction.prediction_score) }">
            {{ getSkillName }}
          </span>
        </div>
        <div class="col col-1 text-end">
          <span class="badge fs-6 ms-1 mb-1 float-end"
            :style="{ 'background-color': colorFromGradient(prediction.prediction_score) }">
            {{ roundScore(prediction.prediction_score) }}%
          </span>
        </div>
      </div>
    </div>
  </td>
</template>

<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'

export default Vue.component('span-extraction', {
  props: ['prediction', 'showWithContext'],
  mixins: [mixin],
  computed: {
    output() {
      let output = this.prediction.prediction_output.output
      if (this.showWithContext) {
        // If there is a prediction document returned use that and ignore local context
        output = this.prediction.prediction_documents[0].document
        // There can be an empty prediction document returned from the skill so use the local context instead
        if (output.length === 0 && this.$store.state.currentContext.length > 0) {
          output = this.$store.state.currentContext
        }
        output = this.highlightSpan(output, this.prediction.prediction_documents[0].span)
      }
      return output
    },
    getSkillName() {
      let availableSkills = this.$store.state.availableSkills;
      // get Skill from availableSkills that matches the skill id
      let skill = availableSkills.filter(skill => skill.id === this.prediction.skill_id)[0];
      return skill.name;
    }
  },
  methods: {
    highlightSpan: function (doc, span) {
      if (span && span[0] !== span[1]) {
        return doc.slice(0, span[0]) + '<mark class="bg-success text-light">' + doc.slice(span[0], span[1]) + '</mark>' + doc.slice(span[1])
      } else {
        return doc
      }
    }
  }
})
</script>
