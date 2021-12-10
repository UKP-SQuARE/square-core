<!-- The Registration Page. The user can register a new account here. -->
<template>
  <div class="d-flex justify-content-center">
    <div class="card border-primary shadow align-self-center text-center" style="width: 362px;">
      <h5 class="card-header fw-light py-2">Sign up</h5>
      <div class="card-body p-4">
        <Alert v-if="success" class="alert-success" dismissible>Your account was created successfully! You can sign in now.</Alert>
        <Alert v-if="failure" class="alert-danger" dismissible>There was a problem: {{ failureMessage }}</Alert>
        <h3 class="card-title mb-3">Sign up now</h3>
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
          <div class="row mt-3">
            <div class="col">
              <button type="submit" class="btn btn-primary w-100">Sign up</button>
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
import { postSignUp } from '@/api'

export default Vue.component('sign-up', {
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      success: false,
      failure: false,
      failureMessage: ''
    }
  },
  components: {
    Alert
  },
  methods: {
    onSubmit() {
      postSignUp(this.form.username, this.form.password)
        .then(() => {
          this.success = true
          this.failure = false
        })
        .catch(failureMessage => {
          this.failure = true
          this.failureMessage = failureMessage
        })
    }
  }
})
</script>
