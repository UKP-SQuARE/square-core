<template>
  <b-container>
    <b-form-row class="mt-5">
      <b-form class="offset-md-1 col-md-10">
        <b-alert v-model="showEmptyWarning" variant="danger" dismissible>
          You need to enter a question!
        </b-alert>
        <b-input-group>
          <b-form-input v-model="inputQuestion" placeholder="What is the air speed of an unladen swallow?"></b-form-input>
          <b-input-group-append>
            <b-button type="submit" variant="primary" v-on:click.prevent="askQuestion">Ask your question</b-button>
          </b-input-group-append>
        </b-input-group>
        <b-form-checkbox v-model="showOptions" switch class="mt-3 ml-1">
          Show expert options
        </b-form-checkbox>
      </b-form>
    </b-form-row>
    <b-form-row v-if="showOptions" class="mt-3">
      <b-form class="offset-md-1 col-md-10">
        <b-form-select v-model="options.selectedSkills" :options="availableSkills" multiple :select-size="Math.min(4, availableSkills.length)"></b-form-select>
      </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
export default {
  name: 'query',
  data() {
    return {
      showOptions: false,
      options: {
        selectedSkills: []
      },
      showEmptyWarning: false,
      inputQuestion: ""
    }
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    }
  },
  methods: {
    askQuestion() {
      if(this.inputQuestion.length > 0){
        this.showEmptyWarning = false
        this.$store.dispatch("answerQuestion", {question: this.inputQuestion, options: this.options})
        .then(() => this.$router.push("/results"))
      } else {
        this.showEmptyWarning = true
      }
    }
  },
  beforeMount(){
    this.$store.dispatch("updateAvailableSkills")
    .then(() => this.options.selectedSkills = this.$store.state.availableSkills)
  }
}
</script>
