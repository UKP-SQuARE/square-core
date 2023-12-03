<template>
  <div> <!-- Root element -->
    <!-- Certificate Preview -->
    <div class="certificate-preview" @click="showModal(certificateId)">
      <h5>{{ certificateTitle }}</h5>
      <!-- Design in progress -->
    </div>

    <!-- Modal -->
    <div v-if="activeModal === certificateId" class="modal fade show" style="display: block;" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="certificateModalLabel">{{ certificateTitle }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div class="card mx-auto my-5 border-0">
              <div class="card-body p-4 bg-light shadow">
                <div class="text-center mb-4">
                  <h3 class="card-title">{{ certificateTitle }}</h3>
                  <p class="text-muted">{{ evaluationType }}</p>
                </div>
                <div class="certificate-body bg-white border p-4">
                  <h5 class="text-center fw-bold">{{ studentName }}</h5>
                  <p class="text-center">has achieved a score of</p>
                  <p class="text-center fw-bold">{{ score }}</p>
                  <div class="text-center mt-4">
                    <p class="text-muted">Issued on {{ issueDate }}</p>
                  </div>
                  <!-- Social Sharing Links -->
                  <div class="text-center mt-4">
                    <a :href="linkedinShareUrl" target="_blank" class="btn btn-outline-primary me-2">
                      Share on LinkedIn
                    </a>
                    <a :href="facebookShareUrl" target="_blank" class="btn btn-outline-primary">
                      Share on Facebook
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeModal" class="modal-backdrop fade show"></div> <!-- Modal backdrop -->
  </div>
</template>

<script>
export default {
  name: 'CertificateCard',
  props: {
    certificateId: {
      type: Number,
      required: true,
      default: 1
    },
    certificateTitle: {
      type: String,
      default: 'LLM Evaluation Certificate'
    },
    studentName: {
      type: String,
      default: 'John Doe'
    },
    score: {
      type: String,
      default: '95%'
    },
    evaluationType: {
      type: String,
      default: 'Language Model Proficiency'
    },
    issueDate: {
      type: String,
      default: 'January 1, 2023'
    }
  },
  data() {
    return {
      activeModal: null,
    };
  },
  methods: {
    showModal(id) {
      this.activeModal = id;
    },
    closeModal() {
      this.activeModal = null;
    }
  }
}
</script>

<style scoped>

.certificate-preview {
  cursor: pointer;
  /* Add your styles for the preview */
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}

/* You might need to adjust the z-index for the modal to make sure it's above the backdrop */
.modal {
  z-index: 1050;
}

.certificate-body {
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
}

</style>
