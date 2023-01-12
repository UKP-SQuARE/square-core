<template>
    <div>
      <div class="card bg-light border border-danger rounded shadow mt-3">
        <div class="card-header bg-transparent p-2">
          <div class="row m-0">
            <div class="col d-flex justify-content-start p-0">
              <slot name="leftItem" />
            </div>
            <div class="col d-flex justify-content-center align-items-center">
              <slot name="topItem"><h5 class="fw-light mb-0">{{ title }}</h5></slot>
            </div>
            <div class="col d-flex justify-content-end p-0">
              <slot name="rightItem" />
            </div>
          </div>
        </div>
        <div class="card-body bg-light">
          <slot />
        </div>
      </div>
    </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('card-view', {
props: ['title']
})
</script>