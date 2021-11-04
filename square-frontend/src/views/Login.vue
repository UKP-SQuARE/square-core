<!-- The Login Page. The user can login here. -->
<template>
  <div class="d-flex justify-content-center">
    <div class="card shadow align-self-center p-3" style="width: 362px;">
      <div class="card-body text-center">
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
          <div class="row">
            <div class="col">
              <button type="submit" class="btn btn-primary w-100">Sign in</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Alert from '@/components/Alert.vue'

export default Vue.component('login', {
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
      this.$store.dispatch('login', {
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
