<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <footer class="py-3 bg-light border-top">
    <div class="container">
      <ul class="nav justify-content-center">
        <li class="nav-item"><router-link to="/terms-and-conditions" class="nav-link px-2 text-muted">Terms and Conditions</router-link></li>
        <li class="nav-item"><a href="https://www.informatik.tu-darmstadt.de/ukp/impressum.en.jsp" class="nav-link px-2 text-muted">Legal Note</a></li>
        <li class="nav-item"><a href="https://www.tu-darmstadt.de/datenschutzerklaerung.en.jsp" class="nav-link px-2 text-muted">Privacy Policy</a></li>
        <li class="nav-item"><a href="https://www.informatik.tu-darmstadt.de/ukp/ukp_home/index.en.jsp" class="nav-link px-2 text-muted">UKP Lab</a></li>
      </ul>
    </div>
  </footer>
</template>

<script>
import Vue from 'vue'

export default Vue.component('square-footer', {
})
</script>
