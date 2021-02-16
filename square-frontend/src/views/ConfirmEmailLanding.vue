<template>
  <b-container >
    <h2 class="text-center">Email Confirmation</h2>
    <hr />
    <b-alert
        v-model="success"
        variant="success"
    >{{successMessage}}</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>
    <b-card
        title="Please confirm your email"
        style="max-width: 20rem;"
        class="mb-2 confirmCard offset-md-4 col-md-4">
      <b-card-text>
        Please confirm your email to start using UKP-SquARES
      </b-card-text>
      <b-button v-on:click="confirm" variant="primary">Confirm</b-button>
    </b-card>

  </b-container>
</template>

<script>
import { confirmEmail } from "@/api";
export default {
name: "confirmEmailLanding",
  data() {
    return {
      success: false,
      failure: false,
      successMessage: "",
      failureMessage: ""
    };
  }, //
  methods: {
      confirm: function (){
        console.log(typeof (this.$route.params.token));
        confirmEmail(this.$route.params.token)
            .then((successMessage) => {
              this.success = true;
              this.successMessage = successMessage.data.message;
            })
            .catch(failureMessage => {
              this.failure = true;
              this.failureMessage = failureMessage.data.message;
            });
      }
    }
};
</script>
