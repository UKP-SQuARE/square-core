<!-- The Registration Page. The user can register a new account here. -->
<template>
  <b-container>
    <h2 class="text-center">Register as a new user</h2>
    <hr />

    <b-alert
      v-model="success"
      variant="success"
    >{{successMessage}}</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>

    <b-form-row v-if="!success">
      <b-form v-on:submit.prevent="onSubmit" class="offset-md-4 col-md-4">
        <b-form-group>
          <b-form-input v-model="form.username" type="text" required placeholder="Username"></b-form-input>
        </b-form-group>
        <b-form-group>
          <b-form-input v-model="form.email" type="text" required placeholder="Email"></b-form-input>
        </b-form-group>
        <b-form-group>
          <b-form-input v-model="form.password" type="password" required placeholder="Password"></b-form-input>
        </b-form-group>
        <b-button type="submit" variant="primary">Register</b-button>
      </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
import { registerUser } from "@/api";
export default {
  name: "register",
  data() {
    return {
      form: {
        username: "",
        password: "",
        email: ""
      },
      success: false,
      failure: false,
      successMessage: "",
      failureMessage: ""
    };
  },
  methods: {
    onSubmit() {
      registerUser(this.form.username, this.form.password, this.form.email)
        .then((successMessage) => {
          this.success = true;
          this.successMessage = successMessage;
        })
        .catch(failureMessage => {
          this.failure = true;
          this.failureMessage = failureMessage;
        });
    }
  }
};
</script>
