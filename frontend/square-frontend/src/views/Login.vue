<template>
  <b-container>
    <h2 class="text-center">Login with your account</h2>
    <hr>
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
            <b-button type="submit" variant="primary">Login</b-button>
        </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
export default {
  name: 'login',
  data() {
      return {
        form: {
            username: "",
            password: ""
        },
        failure: false,
        failureMessage: ""
      }
  },
  methods: {
      onSubmit(){
          this.$store.dispatch("login", {username: this.form.username, password: this.form.password})
          .then(() => {
              this.failure = false
              this.$router.push("/")
              })
          .catch((failureMessage) => {
              this.failure = true
              this.failureMessage = failureMessage
              })
      }
  }
}
</script>
