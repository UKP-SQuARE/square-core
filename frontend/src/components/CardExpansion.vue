<template id="evaluation-item">
    <div class="body" v-show="show">
        <div v-for="(elem, metric_name)  in items" :key="elem.id">
            {{ metric_name }}        
            <div v-for="(value, key) in elem.results" :key="value.id">
                <p class="mb-3">{{ key }} : {{value}}</p>
            </div>
        </div>
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
        this.$root.$on(this.evaluation.skill_id, data => {
            this.show = data
            this.items = this.evaluation.metric_results
        });
    }
  })
  </script>