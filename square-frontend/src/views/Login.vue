<!-- The Login Page. The user can login here. -->
<template>
  <b-container>
    <h2 class="text-center">Login with your account</h2>
    <hr />

    <b-alert v-model="sessionExpired" variant="warning">Session expired. Please login again.</b-alert>
    <b-alert v-model="failure" variant="danger" dismissible>There was a problem: {{failureMessage}}</b-alert>

    <b-form-row>
      <b-form v-on:submit.prevent="onSubmit" class="offset-md-4 col-md-4">
        <b-form-group>
          <b-form-input v-model="form.username" type="text" required placeholder="Username"></b-form-input>
        </b-form-group>
        <b-form-group>
          <b-form-input v-model="form.password" type="password" required placeholder="Password"></b-form-input>
        </b-form-group>
        <b-button type="submit" variant="primary">Login</b-button>
      </b-form>
    </b-form-row>
  </b-container>
</template>

<script>
export default {
  name: "login",
  data() {
    return {
      form: {
        username: "",
        password: ""
      },
      failure: false,
      failureMessage: ""
    };
  },
  methods: {
    onSubmit() {
      this.$store
        .dispatch("login", {
          username: this.form.username,
          password: this.form.password
        })
        .then(() => {
          this.failure = false;
          this.$router.push("/");
        })
        .catch(error => {
          this.failure = true;
          this.failureMessage = error.data.msg;
        });
    }
  },
  computed: {
    sessionExpired() {
      return this.$store.getters.isSessionExpired();
    }
  }
};
</script>
