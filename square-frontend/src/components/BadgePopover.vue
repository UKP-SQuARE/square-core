<template>
  <span
      @mouseover="showPopover"
      v-on:click="showPopover"
      :data-bs-content="popoverContent"
      data-bs-trigger="hover focus"
      data-bs-placement="top"
      class="badge bg-primary d-inline-flex align-items-center mx-2 py-2"
      style="cursor: help">
    {{ popoverTitle }}
  </span>
</template>

<script>
import Vue from 'vue'
import {Popover} from "bootstrap";

export default Vue.component('badge-popover', {
  props: ['popoverTitle', 'popoverContent'],
  methods: {
    showPopover(event) {
      new Popover(event.target).show()
    }
  }
})
</script>
