<!-- The feedback page. -->
<template>
  <div class="d-flex align-items-top">
      <div class="d-flex flex-column flex-md-row w-100 ps-md-3">
        <div class="bg-light flex-fill my-2 me-md-3 pt-3 px-3 pt-md-5 px-md-5 overflow-hidden">
          <div class="mb-3 pb-3">
            <h2 class="display-5">News</h2>
            <div class="container">
            <div class="row" data-masonry='{"percentPosition": true }'>
              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}scadsai.png`" class="card-img-top" alt="ScaDS.AI logo">
                  <div class="card-body">
                    <h5 class="card-title">Machine Learning Summer School</h5>
                    <p class="card-text">SQuARE is presented at the <a href="https://scads.ai/education/summer-schools/scads-ai-summer-school-2022/prof-iryna-gurevychharitz-puerto/" target="_blank">ScaDS.AI Machine Learning Summer School</a> in Leipzig. Check the <a href="https://twitter.com/Sca_DS/status/1546789948644286465" target="_blank">Tweet</a>!</p>
                    <p class="card-text"><small class="text-muted">Jul. 2022</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}acl2022.png`" class="card-img-top" alt="acl logo">
                  <div class="card-body">
                    <h5 class="card-title">ACL 2022</h5>
                    <p class="card-text">SQuARE is presented at ACL as a <a href="https://aclanthology.org/2022.acl-demo.2/" target="_blank">demo paper</a>.</p>
                    <p class="card-text"><small class="text-muted">May 2022</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}SQuARE_Banner.png`" class="card-img-top" alt="SQuARE logo">
                  <div class="card-body">
                    <h5 class="card-title">1st Public Release</h5>
                    <p class="card-text"> SQuARE is publicly launched!</p>
                    <p class="card-text"><small class="text-muted">Mar. 2022</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}podcast.png`" class="card-img-top" alt="Podcast logo">
                  <div class="card-body">
                    <h5 class="card-title">SQuARE in We Decentralize Tech Podcast</h5>
                    <p class="card-text"> Haritz Puerto talks about QA, <a href="https://arxiv.org/abs/2112.01922" target="_blank">MetaQA</a>, and introduces the soon-to-be-launched SQuARE at the <a href="https://anchor.fm/elia-ia/episodes/Ep-14---Haritz-Puerto-UKP-Lab---Haciendo-que-la-IA-resuelva-preguntas-e1ekdgl" target="_blank"> We Decentralize Tech Podcast</a> (in Spanish).</p>
                    <p class="card-text"><small class="text-muted">Feb. 2022</small></p>
                  </div>
                </div>
              </div>

            </div>
              
          </div>

        </div>
      </div>
    </div>
  </div>
</template>


<script>
import Vue from 'vue'

export default Vue.component('show-news', {
   data() {
    return {
      publicPath: process.env.BASE_URL
    }
  },
})
</script>
