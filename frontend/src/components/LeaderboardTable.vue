<template>
  <div class="leaderboard">
    <b-table striped hover :items="displayedData" :fields="fields"></b-table>
    <button @click="toggleFullView" class="btn btn-success btn-sm text-white">
      {{ full ? 'Show Less' : 'Show More' }}
    </button>
  </div>
</template>


<script>
import { getLeaderboard } from '@/api'
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
    getLeaderboard(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let i = 0; i < response.data.length; i++) {
          let position = { id: i, name: response.data[i].email, score: response.data[i].overallPoints }
          this.leaderboardData.push(position)
        }
        this.leaderboardData.sort((a, b) => b.score - a.score); // Sort leaderboardData
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
