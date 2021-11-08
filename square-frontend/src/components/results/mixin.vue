<script>
export default {
  methods: {
    highlightSpan: function (doc, span) {
      return doc.slice(0, span[0]) + '<mark>' + doc.slice(span[0], span[1]) + '</mark>' + doc.slice(span[1])
    },
    roundScore(score) {
      return Math.round(score * 100_000) / 1_000
    }
  }
}
</script>