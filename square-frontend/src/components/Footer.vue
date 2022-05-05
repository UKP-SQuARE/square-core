<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <footer class="py-3 bg-light border-top">
    <div class="container">
      <ul class="nav justify-content-center">
        <li class="nav-item"><router-link to="/terms-and-conditions" class="nav-link px-2 text-muted">Terms and Conditions</router-link></li>
        <li class="nav-item"><a href="https://www.informatik.tu-darmstadt.de/ukp/impressum.en.jsp" class="nav-link px-2 text-muted">Legal Note</a></li>
        <li class="nav-item"><a href="https://www.tu-darmstadt.de/datenschutzerklaerung.en.jsp" class="nav-link px-2 text-muted">Privacy Policy</a></li>
        <li class="nav-item"><a href="https://www.informatik.tu-darmstadt.de/ukp/ukp_home/index.en.jsp" class="nav-link px-2 text-muted">UKP Lab</a></li>
        <li class="nav-item">
          <ul class="navbar-nav me-auto">
                <a class="nav-link px-2 text-muted" href="https://twitter.com/UKP_SQuARE" title="Twitter" target="_blank" width="50">
                  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-twitter" viewBox="0 2 16 16">
                    <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
                  </svg>
                </a>
          </ul>
        </li>
      </ul>
    </div>
    <div class="container">
      <ul class="nav justify-content-center">
        <li class="nav-item"><img :src="`${publicPath}ukp_logo.png`" alt="Ubiquitous Knowledge Processing" width="110" height="40" class="px-2"></li> 
        <li class="nav-item"><img :src="`${publicPath}tud_logo.png`" alt="TU Darmstadt" width="120" height="40" class="px-2"></li>
      </ul>
    </div>
  </footer>
</template>

<script>
import Vue from 'vue'

export default Vue.component('square-footer', {  
  data() {    
    return {
      publicPath: process.env.BASE_URL
    }
  }
})
</script>
