<script>
export default {
  methods: {
    highlightSpan: function (doc, span) {
      if (span) {
        return doc.slice(0, span[0]) + '<mark class="px-0 bg-primary text-light">' + doc.slice(span[0], span[1]) + '</mark>' + doc.slice(span[1])
      } else {
        return doc
      }
    },
    roundScore(score) {
      return Math.round(score * 100_000) / 1_000
    }
  }
}
</script>