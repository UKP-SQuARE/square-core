<!-- The Main View -->
<template>
  <div id="app" class>
    <NavBar></NavBar>
    <router-view />
  </div>
</template>

<script>
import NavBar from "@/components/NavBar.vue";
export default {
  components: {
    NavBar
  },
  beforeMount() {
    this.$store.dispatch("initJWTfromLocalStorage");
  }
};
</script>

<style lang='scss'>
@import "~bootstrap";
@import "~bootstrap-vue";
</style>
