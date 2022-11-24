<!-- Component for the Results. The user can see the results of each chosen skill here. Results can have different formats. -->
<template>
    <td class="pt-4">
        <span v-html="output" />

        <span class="badge fs-6 ms-1 mb-1 float-end" v-on:click="upvote(prediction.prediction_output.output)"
            :disabled="this.upvoted" 
            :style="[!this.upvoted ? { 'background-color': 'rgb(66, 186, 150)', 'cursor':'pointer' } : { 'background-color': 'rgb(128,128,128)' }]">
            &#9650; Upvote
        </span>

        <span class="badge fs-6 ms-1 mb-1 float-end"
            :style="{ 'background-color': colorFromGradient(prediction.prediction_score) }">
            {{ roundScore(prediction.prediction_score) }}%
        </span>
    </td>
</template>
  
<script>
import Vue from 'vue'
import mixin from '@/components/results/mixin.vue'
import 'bootstrap'


export default Vue.component('information-retrieval', {
    props: ['prediction', 'showWithContext'],
    mixins: [mixin],
    data() {
        return {
            upvoted: false
        }
    },
    computed: {
        output() {
            return this.prediction.prediction_output.output
        }
    },
    mounted() {
        this.$root.$on("clearUpvotes", () => {
            this.upvoted = false
        })
    },
    methods: {
        upvote: function (feedbackDoc) {
            this.upvoted = true
            this.$root.$emit('addFeedbackDocument', feedbackDoc);
        }
    }
})
</script>