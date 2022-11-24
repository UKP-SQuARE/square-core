<script>
import Vue from 'vue'

export default Vue.component('results-mixin', {
  methods: {
    roundScore(score, float = true) {
      if (float) {
        return Math.round(score * 10_000) / 100
      } else {
        return Math.round(score * 1_000) / 10
      }
    },
    colorFromGradient(value) {
      let colors = [
        {
          points: 0.0,
          color: { r: 0xde, g: 0x45, b: 0x16 }
        }, {
          points: 0.5,
          color: { r: 0xde, g: 0xac, b: 0x16 }
        }, {
          points: 1.0,
          color: { r: 0x08, g: 0x9e, b: 0x7b }
        }]
      let i = 1
      for (; i < colors.length - 1; i++) {
        if (value < colors[i].points) {
          break;
        }
      }
      let lower = colors[i - 1]
      let upper = colors[i]
      let range = upper.points - lower.points;
      let rangePoints = (value - lower.points) / range;
      let pointsLower = 1 - rangePoints;
      let pointsUpper = rangePoints;
      let color = {
        r: Math.floor(lower.color.r * pointsLower + upper.color.r * pointsUpper),
        g: Math.floor(lower.color.g * pointsLower + upper.color.g * pointsUpper),
        b: Math.floor(lower.color.b * pointsLower + upper.color.b * pointsUpper)
      }
      return `rgb(${color.r}, ${color.g}, ${color.b})`
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