<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
  <div :class="{ 'alert-dismissible': dismissible }" class="alert d-flex align-items-center shadow" role="alert">
    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-exclamation-square-fill" viewBox="0 0 16 16">
      <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6 4c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995A.905.905 0 0 1 8 4zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
    </svg>
    <div class="ms-2"><slot /></div>
    <button v-if="dismissible" type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" />
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('alert-view', {
  props: {
    dismissible: Boolean
  }
})
</script>
