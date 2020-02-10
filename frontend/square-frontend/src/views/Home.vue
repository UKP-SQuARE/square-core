<template>
    <b-container>
        <Query></Query>
        <Results></Results>
    </b-container>
</template>

<script>
import Query from '@/components/Query.vue'
import Results from '@/components/Results.vue'
export default {
  name: "home",
  components: {
      Query, 
      Results
  }
}
</script>