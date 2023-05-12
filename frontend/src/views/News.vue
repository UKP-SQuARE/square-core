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
                  <img :src="`${publicPath}acl2023.png`" class="card-img-top" alt="acl 2023 logo">
                  <div class="card-body">
                    <h5 class="card-title">ACL 2023</h5>
                    <p class="card-text">SQuARE v3 is accepted at ACL as a <a href="https://arxiv.org/abs/2303.18120"
                        target="_blank">demo paper</a>.</p>
                    <p class="card-text"><small class="text-muted">May. 2023</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}odsc_logo.png`" class="card-img-top" alt="ODSC East 2023 Conference logo">
                  <div class="card-body">
                    <h5 class="card-title">ODSC East 2023 Conference</h5>
                    <p class="card-text">Prof. Iryna Gurevych and Haritz Puerto present SQuARE at the <a
                        href="https://odsc.com/speakers/square-towards-multi-domain-and-few-shot-collaborating-question-answering-agents/"
                        target="_blank">Open Data Science East 2023 Conference</a>.</p>
                    <p class="card-text"><small class="text-muted">May. 2023</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}aacl_logo.png`" class="card-img-top" alt="AACL logo">
                  <div class="card-body">
                    <h5 class="card-title">AACL 2022</h5>
                    <p class="card-text">SQuARE v2 is accepted at AACL as a <a href="https://arxiv.org/abs/2208.09316"
                        target="_blank">demo paper</a>.</p>
                    <p class="card-text"><small class="text-muted">Oct. 2022</small></p>
                  </div>
                </div>
              </div>


              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}ellis_logo.png`" class="card-img-top" alt="ELLIS logo">
                  <div class="card-body">
                    <h5 class="card-title">2022 ELLIS PhD Sympsosium</h5>
                    <p class="card-text">SQuARE is presented at the <a href="https://ellisalicante.org/eds2022/"
                        target="_blank">ELLIS PhD Sympsosium</a> in Alicante. Check the <a
                        href="https://twitter.com/UKP_SQuARE/status/1572885615426805760?s=20&t=eQ6TQzLT3dTf85SAT4by8Q"
                        target="_blank">Tweet</a>!</p>
                    <p class="card-text"><small class="text-muted">Sep. 2022</small></p>
                  </div>
                </div>
              </div>


              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}scadsai.png`" class="card-img-top" alt="ScaDS.AI logo">
                  <div class="card-body">
                    <h5 class="card-title">Machine Learning Summer School</h5>
                    <p class="card-text">SQuARE is presented at the <a
                        href="https://scads.ai/education/summer-schools/scads-ai-summer-school-2022/prof-iryna-gurevychharitz-puerto/"
                        target="_blank">ScaDS.AI Machine Learning Summer School</a> in Leipzig. Check the <a
                        href="https://twitter.com/Sca_DS/status/1546789948644286465" target="_blank">Tweet</a>!</p>
                    <p class="card-text"><small class="text-muted">Jul. 2022</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}coliseum.jpg`" class="card-img-top" alt="Coliseum">
                  <div class="card-body">
                    <h5 class="card-title">Sapienza's BabelNet Workshop</h5>
                    <p class="card-text">Prof. Iryna Gurevych presents SQuARE at the <a
                        href="http://mousse-project.org/events/event-a5f3r5.html" target="_blank">BabelNet's
                        10<sup>th</sup> Anniversary Workshop</a></p>
                    <p class="card-text"><small class="text-muted">Jul. 2022</small></p>
                  </div>
                </div>
              </div>

              <div class="col-sm-6 col-lg-4 mb-4">
                <div class="card">
                  <img :src="`${publicPath}acl2022.png`" class="card-img-top" alt="acl logo">
                  <div class="card-body">
                    <h5 class="card-title">ACL 2022</h5>
                    <p class="card-text">SQuARE is presented at ACL as a <a
                        href="https://aclanthology.org/2022.acl-demo.2/" target="_blank">demo paper</a>.</p>
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
                    <p class="card-text"> Haritz Puerto talks about QA, <a href="https://arxiv.org/abs/2112.01922"
                        target="_blank">MetaQA</a>, and introduces the soon-to-be-launched SQuARE at the <a
                        href="https://anchor.fm/elia-ia/episodes/Ep-14---Haritz-Puerto-UKP-Lab---Haciendo-que-la-IA-resuelva-preguntas-e1ekdgl"
                        target="_blank"> We Decentralize Tech Podcast</a> (in Spanish).</p>
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
