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
          <router-link class="nav-link px-2 text-muted" to="/feedback">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-envelope" viewBox="0 1 18 18">
              <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2Zm13 2.383-4.708 2.825L15 11.105V5.383Zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741ZM1 11.105l4.708-2.897L1 5.383v5.722Z"/>
            </svg> Feedback</router-link>
        </li>
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
    <div class="container my-3">
      <ul class="nav justify-content-center">
        <li class="nav-item"><img :src="`${publicPath}ukp_logo.png`" alt="Ubiquitous Knowledge Processing" width=auto height="58" class="px-3"></li> 
        <li class="nav-item"><img :src="`${publicPath}tud_logo.png`" alt="TU Darmstadt" width=auto height="58" class="px-3"></li>
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
