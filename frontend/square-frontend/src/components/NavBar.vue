<template>
  <b-navbar toggleable="lg" type="light">
    <b-navbar-brand to="/">UKP-SQuARE</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-item to="/">Home</b-nav-item>
        <b-nav-item to="/about">About</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto" v-if="!isAuthenticated">
          <b-nav-item to="/register" link-classes="text-dark">Sign up</b-nav-item>
          <b-button variant="outline-primary" to="/login">Login</b-button>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto"  v-else>
        <b-nav-item-dropdown right v-bind:text="user.name">
          <b-dropdown-item to="/skills">My Skills</b-dropdown-item>
          <div class="dropdown-divider"></div>
          <b-dropdown-item v-on:click.prevent="signout" href="#" variant="danger">Sign Out</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>    
</template>

<script>
export default {
  name: 'NavBar',
  computed: {
    user() {
      return this.$store.state.user
    },
    isAuthenticated() {
      return this.$store.getters.isAuthenticated()
    }
  },
  methods: {
    signout() {
      this.$store.dispatch("signout")
      .then(() => this.$router.push("/"))
    }
  }
}
</script>
