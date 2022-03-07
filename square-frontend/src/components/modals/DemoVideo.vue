<template>
  <div>
    <a role="button" class="text-dark" data-bs-toggle="modal" data-bs-target="#modal-demo" @click="playDemoVideo">
      <div
          class="border border-dark rounded bg-dark shadow mx-auto d-inline-flex align-items-center justify-content-center"
          style="width: 100%; max-width: 480px; padding: calc((min(56.25%, 270px) - 50px) / 2) 0; background-size: 100%" :style="{ 'background-image': `url(${publicPath}demo_thumbnail.png)` }">
        <svg xmlns="http://www.w3.org/2000/svg" width="50px" height="50px" fill="currentColor" class="bi bi-play-circle-fill" viewBox="0 0 16 16">
          <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM6.79 5.093A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814l-3.5-2.5z"/>
        </svg>
      </div>
    </a>
    <div class="modal fade" id="modal-demo" data-bs-backdrop="static" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-fullscreen">
        <div class="modal-content bg-black">
          <div class="modal-header border-0">
            <button
                type="button"
                class="btn-close btn-close-white"
                data-bs-dismiss="modal"
                @click="stopDemoVideo"
                aria-label="Close" />
          </div>
          <div class="modal-body p-0 d-flex align-items-center">
            <video controls preload="none" class="w-100 mh-100" ref="demoVideo">
              <source :src="`${publicPath}demo.mp4`"
                      type="video/mp4">
              Sorry, your browser doesn't support embedded videos.
            </video>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('demo-video', {
  data() {
    return {
      publicPath: process.env.BASE_URL
    }
  },
  methods: {
    playDemoVideo() {
      this.$refs.demoVideo.play()
    },
    stopDemoVideo() {
      let media = this.$refs.demoVideo
      media.pause()
      media.currentTime = 0
    }
  }
})
</script>
