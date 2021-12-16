<!-- The Explainability Page. Contains information about this project -->
<template>
  <div>
    <div class="card border-primary shadow">
      <div class="card-body p-4">
        <form v-on:submit.prevent="askQuestion">
          <div class="row">
            <div class="col-lg">
              <div class="row">
                <div class="col">
                  <div class="input-group">
                    <div class="form-floating flex-grow-1">
                      <select v-model="options.selectedSkill" class="form-select rounded-0 rounded-start" id="skillSelect">
                        <option v-for="skill in availableSkills" v-bind:value="skill.id" v-bind:key="skill.id">
                          {{ skill.name }} — {{ skill.description }}
                        </option>
                      </select>
                      <label for="skillSelect" class="form-label col-form-label-sm text-muted">Skill selector</label>
                    </div>
                    <button
                        class="btn btn-lg btn-primary d-inline-flex align-items-center"
                        type="submit"
                        :disabled="waiting">
                      <span v-show="waiting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                      &nbsp;Run Checklist
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
    <div class="accordion border border-primary rounded shadow mt-3">
      <div class="accordion-item">
        <h2 class="accordion-header" id="panelsStayOpen-headingOne">
          <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#panelsStayOpen-collapseOne">
            Change same name in both question and context
            <span class="badge bg-secondary d-inline-flex align-items-center ms-3 py-2">INV</span>
            <span class="badge bg-secondary d-inline-flex align-items-center ms-1 py-2">NER</span>
            <span class="badge bg-danger d-inline-flex align-items-center ms-1 py-2">9.9%</span>
          </button>
        </h2>
        <div
            id="panelsStayOpen-collapseOne"
            class="accordion-collapse collapse">
          <div class="accordion-body">
            <div class="row">
              <div class="col-6 text-center">
                <strong>INV</strong>ariance Test on <strong>NER</strong>
              </div>
              <div class="col-6 text-center">
                Failure rate <sup class="text-danger">14</sup>&frasl;<sub>141</sub> = <strong class="text-danger">9.9%</strong>
              </div>
            </div>
            <div class="row my-3">
              <div class="col-6"><h4>Examples</h4></div>
              <div class="col-6 text-end"><a class="btn btn-outline-secondary">Show all cases</a></div>
            </div>
            <div class="row">
              <div class="col">
                <ul class="list-group overflow-scroll" style="max-height: 50vh">
                  <li class="list-group-item bg-light">
                    <div class="row">
                      <div class="col">
                        <strong>Question:</strong> <span v-html="highlightReplacement('Kayla', 'Kimberly', 'What company no longer trades as Kimberly ?')" />
                      </div>
                    </div>
                    <div class="row my-3">
                      <div class="col">
                        <strong>Context:</strong> <small v-html="highlightReplacement('Kayla', 'Kimberly', 'Formed in November 1990 by the equal merger of Kimberly Television and British Satellite Broadcasting , BSkyB became the UK \'s largest digital subscription television company . Following BSkyB \'s 2014 acquisition of Kimberly Italia and a majority 90.04 % interest in Kimberly Deutschland in November 2014 , its holding company British Kimberly Broadcasting Group plc changed its name to Kimberly plc . The United Kingdom operations also changed the company name from British Kimberly Broadcasting Limited to Kimberly UK Limited , still trading as Kimberly .')" />
                      </div>
                    </div>
                    <div class="row">
                      <div class="col">
                        <strong>Prediction:</strong> <span v-html="highlightReplacement('Kayla UK Limited', 'Kimberly UK Limited', 'Kimberly UK Limited')" />
                      </div>
                    </div>
                  </li>
                  <li class="list-group-item bg-light">
                    <div class="row">
                      <div class="col">
                        <strong>Question:</strong> <span v-html="highlightReplacement('Kayla', 'Karen', 'How much did Karen bid to win the 4 broadcast pacakges they bought ?')" />
                      </div>
                    </div>
                    <div class="row my-3">
                      <div class="col">
                        <strong>Context:</strong> <small v-html="highlightReplacement('Kayla', 'Karen', 'Following a lengthy legal battle with the European Commission , which deemed the exclusivity of the rights to be against the interests of competition and the consumer , BSkyB \'s monopoly came to an end from the 2007–08 season . In May 2006 , the Irish broadcaster Setanta Sports was awarded two of the six Premier League packages that the English FA offered to broadcasters . Karen picked up the remaining four for £ 1.3bn . In February 2015 , Karen bid £ 4.2bn for a package of 120 premier league games across the three seasons from 2016 . This represented an increase of 70 % on the previous contract and was said to be £ 1bn more than the company had expected to pay . The move has been followed by staff cuts , increased subscription prices ( including 9 % in Karen \'s family package ) and the dropping of the 3D channel .')" />
                      </div>
                    </div>
                    <div class="row">
                      <div class="col">
                        <strong>Prediction:</strong> <span v-html="highlightReplacement('£4.2bn', '£1.3bn', '£1.3bn')" />
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="accordion-item">
        <h2 class="accordion-header">
          <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#panelsStayOpen-collapseTwo">
            Another awesome test
            <span class="badge bg-secondary d-inline-flex align-items-center ms-3 py-2">MFT</span>
            <span class="badge bg-secondary d-inline-flex align-items-center ms-1 py-2">NER</span>
            <span class="badge bg-danger d-inline-flex align-items-center ms-1 py-2">0.0%</span>
          </button>
        </h2>
        <div id="panelsStayOpen-collapseTwo" class="accordion-collapse collapse">
          <div class="accordion-body" />
        </div>
      </div>
      <div class="accordion-item">
        <h2 class="accordion-header">
          <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#panelsStayOpen-collapseThree">
            Third demo test
            <span class="badge bg-secondary d-inline-flex align-items-center ms-3 py-2">DIR</span>
            <span class="badge bg-secondary d-inline-flex align-items-center ms-1 py-2">NER</span>
            <span class="badge bg-danger d-inline-flex align-items-center ms-1 py-2">0.0%</span>
          </button>
        </h2>
        <div id="panelsStayOpen-collapseThree" class="accordion-collapse collapse">
          <div class="accordion-body" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.component('explainability-page', {
  data() {
    return {
      waiting: false,
      options: {
        selectedSkill: ''
      }
    }
  },
  computed: {
    availableSkills() {
      return this.$store.state.availableSkills
    }
  },
  methods: {
    highlightReplacement: function (source, target, doc) {
      return doc.replaceAll(target, `<mark class="bg-warning">${source}</mark><span class="d-inline-flex align-items-center px-1">
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H4.5z"/>
</svg></span><mark class="bg-success text-light">${target}</mark>`)
    }
  },
  /**
   * Make the store update the skills and init the explain options
   */
  beforeMount() {
    this.$store.dispatch('updateSkills')
        .then(() => {
          this.$store.commit('initExplainOptions', {})
        })
        .then(() => {
          // Copy the object so we do not change the state before a query is issued
          this.options = JSON.parse(
              JSON.stringify(this.$store.state.explainOptions)
          )
        })
  }
})
</script>