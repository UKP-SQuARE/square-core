<template>
  <div id="app" class="container">
    <nav id="nav" class="navbar navbar-light navbar-expand-lg">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
        <li class="nav-item"><router-link class="nav-link" to="/about">About</router-link></li>
        <li class="nav-item"><router-link class="nav-link" to="/results">Results</router-link></li>
      </ul>
    </nav>
    <router-view/>
  </div>
</template>

<style lang='scss'>
@import '~bootstrap';
@import '~bootstrap-vue';
</style>
