<template>
  <div class="leaderboard">
    <b-table striped hover :items="displayedData" :fields="fields"></b-table>
    <button @click="toggleFullView">
      {{ full ? 'Show Less' : 'Show More' }}
    </button>
  </div>
</template>


<script>
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
        { id: 1, name: 'Alice', score: 98 },
        { id: 2, name: 'Bob', score: 95 },
        // ... more entries ...
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
  }
};
</script>

<style scoped>
.leaderboard {
  max-height: 400px; /* Adjust as needed */
  overflow-y: auto;
}
</style>
