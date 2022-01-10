<!-- The Login Page. The user can login here. -->
<template>
  <div class="d-flex justify-content-center">
    <div class="card border-primary shadow align-self-center text-center" style="width: 362px;">
      <h5 class="card-header fw-light py-2">Sign in</h5>
      <div class="card-body p-4">
        <Alert v-if="sessionExpired" class="alert-warning" dismissible>Session expired. Please sign in again.</Alert>
        <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
        <h3 class="card-title mb-3">Please sign in</h3>
        <form v-on:submit.prevent="onSubmit">
          <div class="row">
            <div class="col">
              <div class="form-floating">
                <input v-model="form.username" type="text" class="form-control rounded-0 rounded-top" id="username" placeholder="Username">
                <label for="username">Username</label>
              </div>
              <div class="form-floating">
                <input v-model="form.password" type="password" class="form-control rounded-0 rounded-bottom border-top-0" id="password" placeholder="Password">
                <label for="password">Password</label>
              </div>
            </div>
          </div>
          <div class="row my-3">
            <div class="col">
              <div class="form-check d-inline-block">
                <input v-model="form.remember" class="form-check-input" type="checkbox" value="" id="remember" disabled>
                <label class="form-check-label" for="remember">Remember me</label>
              </div>
            </div>
          </div>
          <div class="row my-3">
            <div class="col">
              <button type="submit" class="btn btn-primary w-100">Sign in</button>
            </div>
          </div>
        </form>
        <div class="row">
          <div class="col">
            <h5>Don't have an account?</h5>
          </div>
        </div>
        <div class="row mt-1">
          <div class="col">
            <router-link to="/signup" role="button" class="btn btn-outline-primary w-100">Sign up</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'

export default Vue.component('sign-in', {
  data() {
    return {
      form: {
        username: '',
        password: '',
        remember: false
      },
      failure: false,
      failureMessage: ''
    }
  },
  components: {
    Alert
  },
  methods: {
    onSubmit() {
      this.$store.dispatch('signIn', {
        username: this.form.username,
        password: this.form.password
      }).then(() => {
        this.failure = false
        this.$router.push('/')
      }).catch(error => {
        this.failure = true
        this.failureMessage = error.data.msg
      })
    }
  },
  computed: {
    sessionExpired() {
      return this.$store.getters.isSessionExpired()
    }
  }
})
</script>
