<!-- The feedback page. -->
<template>
  <div class="d-flex align-items-center">
      <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
          <div class="mb-3 pb-3">
            <div class="feature-icon bg-primary bg-gradient">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-envelope-paper-heart" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1.133l.941.502A2 2 0 0 1 16 5.4V14a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V5.4a2 2 0 0 1 1.059-1.765L2 3.133V2Zm0 2.267-.47.25A1 1 0 0 0 1 5.4v.817l1 .6v-2.55Zm1 3.15 3.75 2.25L8 8.917l1.25.75L13 7.417V2a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v5.417Zm11-.6 1-.6V5.4a1 1 0 0 0-.53-.882L14 4.267v2.55ZM8 2.982C9.664 1.309 13.825 4.236 8 8 2.175 4.236 6.336 1.31 8 2.982Zm7 4.401-4.778 2.867L15 13.117V7.383Zm-.035 6.88L8 10.082l-6.965 4.18A1 1 0 0 0 2 15h12a1 1 0 0 0 .965-.738ZM1 13.116l4.778-2.867L1 7.383v5.734Z"/>
              </svg>
            </div>
            <h2 class="display-5">Share your thoughts</h2>
            <p class="lead fs-2">Do you have <span class="text-primary">thoughts</span> or <span class="text-primary">ideas</span>? Please send us an email!</p>
            <div class="d-grid gap-2 d-lg-flex justify-content-lg-center">
              <a href="mailto:ribeiro@aiphes.tu-darmstadt.de?subject=SQuARE Feedback" class="btn btn-outline-primary btn-lg px-4">Contact us</a>
            </div>
          </div>
        </div>
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
          <div class="mb-3 pb-3">
            <div class="feature-icon bg-danger bg-gradient">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-bug" viewBox="0 0 16 16">
                <path d="M4.355.522a.5.5 0 0 1 .623.333l.291.956A4.979 4.979 0 0 1 8 1c1.007 0 1.946.298 2.731.811l.29-.956a.5.5 0 1 1 .957.29l-.41 1.352A4.985 4.985 0 0 1 13 6h.5a.5.5 0 0 0 .5-.5V5a.5.5 0 0 1 1 0v.5A1.5 1.5 0 0 1 13.5 7H13v1h1.5a.5.5 0 0 1 0 1H13v1h.5a1.5 1.5 0 0 1 1.5 1.5v.5a.5.5 0 1 1-1 0v-.5a.5.5 0 0 0-.5-.5H13a5 5 0 0 1-10 0h-.5a.5.5 0 0 0-.5.5v.5a.5.5 0 1 1-1 0v-.5A1.5 1.5 0 0 1 2.5 10H3V9H1.5a.5.5 0 0 1 0-1H3V7h-.5A1.5 1.5 0 0 1 1 5.5V5a.5.5 0 0 1 1 0v.5a.5.5 0 0 0 .5.5H3c0-1.364.547-2.601 1.432-3.503l-.41-1.352a.5.5 0 0 1 .333-.623zM4 7v4a4 4 0 0 0 3.5 3.97V7H4zm4.5 0v7.97A4 4 0 0 0 12 11V7H8.5zM12 6a3.989 3.989 0 0 0-1.334-2.982A3.983 3.983 0 0 0 8 2a3.983 3.983 0 0 0-2.667 1.018A3.989 3.989 0 0 0 4 6h8z"/>
              </svg>
            </div>
            <h2 class="display-5">Technical Feedback</h2>
            <p class="lead fs-2">To request <span class="text-danger">features</span> or report a <span class="text-danger"> bug</span> you can also use GitHub Issues</p>
            <div class="d-grid gap-2 d-lg-flex justify-content-lg-center">
              <a href="https://github.com/UKP-SQuARE/square-core/issues" target="_blank" class="btn btn-outline-danger btn-lg px-4">GitHub Issues</a>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('send-feedback', {})
</script>