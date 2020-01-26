<template>
  <div id="app" class="">
    <NavBar> </NavBar>
    <router-view/>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
export default {
  components: {
    NavBar
  }
}
</script>

<style lang='scss'>
@import '~bootstrap';
@import '~bootstrap-vue';
</style>
