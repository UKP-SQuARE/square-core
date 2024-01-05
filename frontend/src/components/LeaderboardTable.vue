<template>
  <div class="leaderboard">
    <b-table striped hover :items="displayedData" :fields="fields"></b-table>
    <button @click="toggleFullView">
      {{ full ? 'Show Less' : 'Show More' }}
    </button>
  </div>
</template>


<script>
import { getPositions } from '@/api'
export default {
  name: 'LeaderboardTable',
  props: {
    full: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      leaderboardData: [
        //first empty
      ],
    };
  },
  computed: {
    fields() {
      return [
        { key: 'name', label: 'Name' },
        { key: 'score', label: 'Score' }
      ];
    },
    displayedData() {
      return this.full ? this.leaderboardData : this.leaderboardData.slice(0, 5);
    }
  },
  methods: {
    toggleFullView() {
      this.$emit('update:full', !this.full);
    }
  },
  beforeMount() {
    getPositions(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let i = 0; i < response.data.length; i++) {
          let position = { id: response.data[i].id, name: response.data[i].name, score: response.data[i].score }
          this.leaderboardData.push(position)
        }
      })
      .catch((error) => {
      console.error("Error fetching leaderboard positions:", error);
    });
  }
};
</script>

<style scoped>
.leaderboard {
  max-height: 400px; /* Adjust as needed */
  overflow-y: auto;
}
</style>
