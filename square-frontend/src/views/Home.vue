<!-- The landing page. Contains information about this project -->
<template>
  <div>
    <div class="bg-primary bg-gradient text-white">
      <div class="container-sm text-center py-5">
        <h1 class="display-1 fw-bold">UKP-SQuARE</h1>
        <p class="fs-3">Software for Question Answering Research</p>
        <p class="leader">Watch our demo video to learn more</p>
        <DemoVideo />
        <div class="d-grid gap-2 d-flex justify-content-center mt-5">
          <a
              href="https://arxiv.org"
              target="_blank"
              role="button"
              class="btn btn-light btn-lg px-4 d-flex justify-content-center align-items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-book" viewBox="0 0 16 16">
              <path d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"/>
            </svg>
            &nbsp;Read the paper
          </a>
        </div>
      </div>
    </div>
    <div class="container-xl my-2">
      <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
          <div class="mb-3 pb-3">
            <div class="feature-icon bg-danger bg-gradient">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-question-lg" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M4.475 5.458c-.284 0-.514-.237-.47-.517C4.28 3.24 5.576 2 7.825 2c2.25 0 3.767 1.36 3.767 3.215 0 1.344-.665 2.288-1.79 2.973-1.1.659-1.414 1.118-1.414 2.01v.03a.5.5 0 0 1-.5.5h-.77a.5.5 0 0 1-.5-.495l-.003-.2c-.043-1.221.477-2.001 1.645-2.712 1.03-.632 1.397-1.135 1.397-2.028 0-.979-.758-1.698-1.926-1.698-1.009 0-1.71.529-1.938 1.402-.066.254-.278.461-.54.461h-.777ZM7.496 14c.622 0 1.095-.474 1.095-1.09 0-.618-.473-1.092-1.095-1.092-.606 0-1.087.474-1.087 1.091S6.89 14 7.496 14Z"/>
              </svg>
            </div>
            <h2 class="display-5">Question Answering</h2>
            <p class="lead fs-2">Use or create skills to <span class="text-danger">query</span> and <span class="text-danger">compare</span> models and datastores</p>
            <div class="d-grid gap-2 d-lg-flex justify-content-lg-center">
              <router-link class="btn btn-outline-danger btn-lg px-4" to="/qa">Get started</router-link>
              <a href="/docs/home/components/skills" target="_blank" class="btn btn-outline-danger btn-lg px-4">Learn more</a>
            </div>
          </div>
        </div>
        <div class="bg-primary bg-gradient flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center text-white overflow-hidden">
          <div class="my-3 py-3">
            <h2 class="display-5">Models</h2>
            <p class="lead fs-4">Our platform supports <strong>HuggingFace Transformers</strong>, <strong>Adapters</strong>, <strong>Sentence-Transformers</strong>, and a selection of <strong>ONNX</strong> models</p>
            <a href="/docs/home/components/models" target="_blank" class="btn btn-light btn-lg px-4">Learn more</a>
          </div>
        </div>
      </div>
      <div class="d-flex flex-column-reverse flex-md-row w-100 ps-md-3">
        <div class="bg-primary bg-gradient flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center text-white overflow-hidden">
          <div class="my-3 py-3">
            <h2 class="display-5">Datastores</h2>
            <p class="lead fs-4">We provide datastores for <strong>Wikipedia</strong>, <strong>PubMed</strong>, and <strong>Bing web documents</strong> with more to come</p>
            <a href="/docs/home/components/datastores" target="_blank" class="btn btn-light btn-lg px-4">Learn more</a>
          </div>
        </div>
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
          <div class="mb-3 pb-3">
            <div class="feature-icon bg-success bg-gradient">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            </div>
            <h2 class="display-5">Explainability</h2>
            <p class="lead fs-3">Compare skills through pre-defined <span class="text-success">behavioural tests</span> via CheckList</p>
            <div class="d-grid gap-2 d-lg-flex justify-content-lg-center">
              <router-link class="btn btn-outline-success btn-lg px-4" to="/explain">Get started</router-link>
              <a href="/docs/home/components/explainability" target="_blank" class="btn btn-outline-success btn-lg px-4">Learn more</a>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center overflow-hidden">
          <div class="mb-3 pb-3">
            <h2 class="display-5">Open Source</h2>
            <p class="lead fs-2">Learn more through our <span class="text-warning">Documentation</span> and on <span class="text-warning">GitHub</span></p>
            <div class="d-grid gap-2 d-flex justify-content-center">
              <a href="/docs/" target="_blank" class="btn btn-outline-warning btn-lg px-4">Docs</a>
              <a href="https://github.com/UKP-SQuARE/square-core" target="_blank" class="btn btn-outline-warning btn-lg px-4 d-inline-flex align-items-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
        <div class="bg-primary bg-gradient flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 text-center text-white overflow-hidden">
          <div class="mb-3 pb-3">
            <h2 class="display-5">Social</h2>
            <p class="lead fs-3">Follow us on Twitter</p>
            <a href="https://twitter.com/ukplab" target="_blank" class="fs-1 text-white d-inline-flex align-items-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-twitter" viewBox="0 0 16 16">
                <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import DemoVideo from '@/components/modals/DemoVideo.vue'

export default Vue.component('landing-page', {
  components: {
    DemoVideo
  },
})
</script>