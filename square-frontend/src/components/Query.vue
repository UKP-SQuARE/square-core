<!-- Component for the Search Query. The user can enter a question here and change the query options. -->
<template>
  <b-container>
    <b-form-row class="mt-5">
      <b-form class="offset-md-1 col-md-10" v-on:submit.prevent="askQuestion">
        <b-alert
          v-model="showEmptyWarning"
          variant="danger"
          dismissible
        >You need to enter a question!</b-alert>
        <b-alert
          v-model="failure"
          variant="danger"
          dismissible
        >There was a problem: {{failureMessage}}</b-alert>

        <b-input-group>
          <b-form-input v-model="inputQuestion" required placeholder="Enter your question"></b-form-input>
          <b-input-group-append>
            <b-button type="submit" variant="primary">
              Ask your question
              <b-spinner v-show="waitingQuery" small label="Spinning"></b-spinner>
            </b-button>
          </b-input-group-append>
        </b-input-group>
        <b-form-checkbox v-model="showOptions" switch class="mt-2 ml-1 mb-2">Show expert options</b-form-checkbox>

        <div v-show="showOptions">
          <b-form-group label="Query Mode:">
            <b-form-radio-group v-model="options.action" name="radio-sub-component">
              <b-form-radio
                value="SOCKET_query"
              >WebSocket - receive results as soon as each is available</b-form-radio>
              <b-form-radio value="query">AJAX - receive results once all are available</b-form-radio>
            </b-form-radio-group>
          </b-form-group>
          <b-form-group label="Skill Selector:" label-for="skill-selector">
            <b-form-select
              id="skill-selector"
              v-model="options.selector"
              :options="availableSkillSelectors"
            ></b-form-select>
          </b-form-group>
          <b-form-group label="Only use these skills:" label-for="skill-select">
            <b-form-select
              id="skill-select"
              v-model="options.selectedSkills"
              :options="availableSkills"
              multiple
              :select-size="Math.min(4, availableSkills.length)"
            ></b-form-select>
          </b-form-group>
          <b-form-group label="Maximum number of querried skills:" label-for="max-querried-skills">
            <b-form-input
              id="max-querried-skills"
              v-model="options.maxQuerriedSkills"
              required
              type="number"
            ></b-form-input>
          </b-form-group>
          <b-form-group label="Maximum number of results per skill:" label-for="max-results-skill">
            <b-form-input
              id="max-results-skill"
              v-model="options.maxResultsPerSkill"
              required
              type="number"
            ></b-form-input>
          </b-form-group>
        </div>
      </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
export default {
  name: "query",
  data() {
    return {
      showOptions: false,
      waitingQuery: false,
      options: {
        selectedSkills: []
      },
      showEmptyWarning: false,
      inputQuestion: "",
      failure: false,
      failureMessage: ""
    };
  },
  computed: {
    /**
     * Map state.availableSkills in the format for Vue Bootstrap
     */
    availableSkills() {
      return this.$store.state.availableSkills.map(skill => {
        return {
          text: `${skill.name} ${
            skill.description ? "- " + skill.description : ""
          }`,
          value: skill
        };
      });
    },
    availableSkillSelectors() {
      return this.$store.state.availableSkillSelectors;
    },
    queryOptions() {
      return this.$store.state.queryOptions;
    }
  },
  methods: {
    askQuestion() {
      if (this.inputQuestion.length > 0) {
        this.showEmptyWarning = false;
        this.waitingQuery = true;
        var action = this.options.action;
        if (action === "query") {
          this.$store
            .dispatch(action, {
              question: this.inputQuestion,
              options: this.options
            })
            .catch(error => {
              this.failure = true;
              this.failureMessage = error.data.msg;
            })
            .finally(() => {
              this.waitingQuery = false;
              // Collapse the options once results are here to save space. This is due to query and results residing in one view.
              this.showOptions = false;
            });
        } else if (action === "SOCKET_query") {
          this.$store
            .dispatch(action, {
              question: this.inputQuestion,
              options: this.options
            })
        }
        
      } else {
        this.showEmptyWarning = true;
      }
    }
  },
  /**
   * Make the store update the skills and init the query options
   * Subscribe to mutation changes for the websocket
   */
  beforeMount() {
    var self = this
    this.$store.subscribe(mutation => {
      if (mutation.type === "SOCKET_SKILLRESULT") {
        this.showOptions = false;
        if (mutation.payload.error_msg) {
          self.failure = true;
          self.failureMessage = mutation.payload.error_msg;
          self.waitingQuery = false;
        }
        if (mutation.payload.finished) {
          self.waitingQuery = false;
        }
      }
    })

    this.$store
      .dispatch("updateSkills")
      .then(() => this.$store.dispatch("updateSelectors"))
      .then(() => {
        this.$store.commit("initQueryOptions", {});
      })
      .then(() => {
        // Copy the object so we do not change the state before a query is issued
        this.options = JSON.parse(
          JSON.stringify(this.$store.state.queryOptions)
        );
      });
  }
};
</script>
