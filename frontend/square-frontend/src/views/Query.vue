<template>
  <b-container>
    <b-form-row class="mt-5">
      <b-form class="offset-md-1 col-md-10" v-on:submit.prevent="askQuestion">
        <b-alert v-model="showEmptyWarning" variant="danger" dismissible>
          You need to enter a question!
        </b-alert>
        <b-input-group>
          <b-form-input v-model="inputQuestion" required placeholder="What is the air speed of an unladen swallow?"></b-form-input>
          <b-input-group-append>
            <b-button type="submit" variant="primary">Ask your question</b-button>
          </b-input-group-append>
        </b-input-group>
        <b-form-checkbox v-model="showOptions" switch class="mt-3 ml-1">
          Show expert options
        </b-form-checkbox>
        
    <div v-show="showOptions">
        <b-form-group label="Only use these skills:" label-for="skill-select">
          <b-form-select id="skill-select" v-model="options.selectedSkills" :options="availableSkills" multiple   :select-size="Math.min(4, availableSkills.length)"></b-form-select>
        </b-form-group>
        <b-form-group label="Maximum number of querried skills:" label-for="max-querried-skills">
          <b-form-input
            id="max-querried-skills"
            v-model="options.maxQuerriedSkills"
            required
            type="number"
            v-bind:placeholder="options.maxQuerriedSkills"
          ></b-form-input>
        </b-form-group>
        <b-form-group label="Maximum number of results per skill:" label-for="max-results-skill">
          <b-form-input
            id="max-results-skill"
            v-model="options.maxResultsPerSkill"
            required
            type="number"
            v-bind:placeholder="options.maxResultsPerSkill"
          ></b-form-input>
        </b-form-group>
    </div>
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
        selectedSkills: [],
        maxQuerriedSkills: 3,
        maxResultsPerSkill: 10
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
