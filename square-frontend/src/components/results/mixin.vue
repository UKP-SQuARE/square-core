<script>
import Vue from 'vue'

export default Vue.component('results-mixin', {
  methods: {
    highlightSpan: function (doc, span) {
      if (span) {
        return doc.slice(0, span[0]) + '<mark class="px-0 bg-primary text-light">' + doc.slice(span[0], span[1]) + '</mark>' + doc.slice(span[1])
      } else {
        return doc
      }
    },
    roundScore(score, float = true) {
      if (float) {
        return Math.round(score * 10_000) / 100
      } else {
        return Math.round(score * 1_000) / 10
      }
    },
    mapTestType(shorthand) {
      let map = {
        'MFT': 'Min Func Test',
        'INV': 'INVariance',
        'DIR': 'DIRectional'
      }
      if (shorthand in map) {
        return map[shorthand]
      } else {
        return shorthand
      }
    }
  }
})
</script>