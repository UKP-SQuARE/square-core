<template>
  <b-container>
    <h2 class="text-center">Register as a new user</h2>
    <hr>
    <b-alert v-model="success" variant="success">
        Account was created successfully! You can log in now.
    </b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>
        There was a problem: {{failureMessage}}
    </b-alert>
    <b-form-row v-if="!success">
        <b-form v-on:submit.prevent="onSubmit" class="offset-md-4 col-md-4">
            <b-form-group>
              <b-form-input
              v-model="form.username"
              type="text"
              required
              placeholder="Username">
              </b-form-input>
            </b-form-group>
            <b-form-group>
              <b-form-input
              v-model="form.password"
              type="password"
              required
              placeholder="Password">
              </b-form-input>
            </b-form-group>
            <b-button type="submit" variant="primary">Register</b-button>
        </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
import {registerUser} from "@/api"
export default {
  name: 'register',
  data() {
      return {
        form: {
            username: "",
            password: ""
        },
        success: false,
        failure: false,
        failureMessage: ""
      }
  },
  methods: {
      onSubmit(){
          registerUser(this.form.username, this.form.password)
          .then(() => {
              this.success = true
              this.failure = false
              })
          .catch((failureMessage) => {
              this.failure = true
              this.failureMessage = failureMessage
              })
      }
  }
}
</script>
