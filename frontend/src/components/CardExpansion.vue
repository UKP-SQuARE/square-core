<template id="evaluation-item">
    <div v-if="evaluation_status=='FINISHED'" class="body" v-show="show">
        <li v-for="(value, single_metric)  in items" :key="single_metric">
            {{single_metric }}: {{value }}
        </li>
    </div>
    <div v-else class="body" v-show="show">
        {{evaluation_error}}
    </div>
  </template>
  <script>
  import Vue from 'vue'
  
  export default Vue.component('card-expansion', {
    template: '#evaluation-item',
    props: ['evaluation'],
    data() {
        return {
            show: true,
            items: [],
            evaluation_status:  "",
            evaluation_error: ""
        }
    },
    mounted() {
        this.$root.$on(this.evaluation.evaluation_id, data => {
            this.show = data
            this.items = this.evaluation.metric_result
            this.evaluation_status = this.evaluation.evaluation_status
            this.evaluation_error = this.evaluation.evaluation_error
        });
    }
  })
  </script>