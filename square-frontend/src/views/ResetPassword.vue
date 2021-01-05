<!--
The Reset Password Page.
The user fills the registered email id and request the reset link

-->
<template>
  <b-container>
    <h2 class="text-center">New Password</h2>
    <hr />

    <b-alert
        v-model="success"
        variant="success"
    >{{successMessage}}</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>

    <b-form-row v-if="!success">
      <b-form v-on:submit.prevent="onSubmit" class="offset-md-4 col-md-4">
        <b-form-group>
          <b-form-input v-model="form.password" type="password" required ></b-form-input>
        </b-form-group>
        <b-button type="submit" variant="primary">Reset Password</b-button>
      </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
import { validatenewPassword } from "@/api";
export default {
  name: "resetPassword",
  data() {
    return {
      form: {
        password:""
      },
      success: false,
      failure: false,
      successMessage: "",
      failureMessage: ""
    };
  },
  methods: {
    onSubmit() {
      validatenewPassword(this.$route.params.token, this.form.password)
          .then((successMessage) => {
            this.success = true;
            this.successMessage = successMessage.data.message;
            //this.$router.push("Login")
          })
          .catch(failureMessage => {
            this.failure = true;
            this.failureMessage = failureMessage.data.message;
          });
    }
  }
};
</script>
