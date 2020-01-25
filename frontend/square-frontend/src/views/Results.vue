<template>
  <div class="">
      <div v-for="(res, i) in results" v-bind:key="i"> 
        <div class="card">
            <div class="card-body">
              <p class="card-text">{{ res }}
              </p>
            </div>
        </div>
      </div>
  </div>
</template>

<script>
import { fetchResults } from '@/api'

export default {
  name: 'results',
  data() {
      return {results: []}
  },
  beforeMount() {
      fetchResults().then(response => {this.results = response})
  }
}
</script>
