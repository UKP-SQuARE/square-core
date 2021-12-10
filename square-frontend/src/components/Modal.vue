<template>
  <div>
    <a
        role="button"
        class="btn btn-outline-danger d-inline-flex align-items-center"
        data-bs-toggle="modal"
        :data-bs-target="`#modal-${callbackValue}`"
        :disabled="waiting">
      <span v-if="waiting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
      <span v-if="waiting">&nbsp;</span>
      {{ destructiveActionUpper }}
    </a>
    <div class="modal fade" :id="`modal-${callbackValue}`" tabindex="-1" aria-hidden="true" :ref="`modal-${callbackValue}`">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Are you sure?</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Please confirm that you want to {{ destructiveAction }} <strong>{{ skill }}</strong>.
          </div>
          <div class="modal-footer">
            <a role="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</a>
            <a
                role="button"
                class="btn btn-danger"
                data-bs-dismiss="modal"
                @click="$emit('callback', callbackValue)">
              {{ destructiveActionUpper }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('destructive-action-modal', {
  props: {
    waiting: {
      type: Boolean,
      default: false
    },
    destructiveAction: String,
    skill: String,
    callback: Function,
    callbackValue: String
  },
  computed: {
    destructiveActionUpper() {
      return this.destructiveAction.charAt(0).toUpperCase() + this.destructiveAction.slice(1)
    }
  }
})
</script>