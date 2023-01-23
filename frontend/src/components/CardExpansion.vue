<template id="evaluation-item">
    <div class="body" v-show="show">
        <li v-for="(value, single_metric)  in items" :key="single_metric">
            {{single_metric }}: {{value }}
        </li>
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
            items: []
        }
    },
    mounted() {
        this.$root.$on(this.evaluation.evaluation_id, data => {
            this.show = data
            this.items = this.evaluation.metric_result
        });
    }
  })
  </script>