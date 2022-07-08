<template>
  <div
    id="container"
    class="d-flex flex-column justify-content-center align-items-center"
  >
    <h1>Data flow Graph</h1>
    <h4 v-if="loading">Loading</h4>
    <h4 v-if="error" class="text-danger">{{ error }}</h4>
    <div id="cy" class="cy"></div>
  </div>
</template>


<script>
import cydagre from "cytoscape-dagre";
import cytoscape from "cytoscape";

const nodes = [
  {
    data: {
      id: 0,
      name: "Animal",
      description: "",
      active: true,
      width: 140,
    },
  },
  {
    data: {
      id: 1,
      name: "Mammal",
      description: "",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 2,
      name: "Reptile",
      description: "",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 3,
      name: "Horse",
      description: "",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 4,
      name: "Dog",
      description: "Join",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 5,
      name: "Goat",
      description: "Branch Out",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 6,
      name: "Hound",
      description: "",
      active: false,
      width: 140,
    },
  },
  {
    data: {
      id: 7,
      name: "German Shephard",
      description: "",
      active: false,
      width: 140,
    },
  },
];

const edges = [
  { data: { source: 0, target: 1, label: "Sub" } },
  { data: { source: 0, target: 2, label: "Sub" } },
  { data: { source: 1, target: 3, label: "Sub" } },
  { data: { source: 1, target: 4, label: "Sub" } },
  { data: { source: 1, target: 5, label: "Sub" } },
  { data: { source: 4, target: 6, label: "Sub" } },
  { data: { source: 4, target: 7, label: "Sub" } },
];

export default {
  name: "DataFlow",
  data() {
    return {
      loading: false,
      error: null,
    };
  },
  mounted() {
    this.drawGraph();
  },
  methods: {
    drawGraph() {
      cydagre(cytoscape);
      const cy = cytoscape({
        container: document.getElementById("cy"),
        boxSelectionEnabled: false,
        autounselectify: true,
        style: cytoscape
          .stylesheet()
          .selector("node")
          .css({
            shape: "roundrectangle",
            height: 40,
            width: "data(width)",
            "background-color": (node) =>
              node.data("active") ? "green" : "white",
            color: (node) => (node.data("active") ? "white" : "black"),
            "border-color": "gray",
            "border-width": 3,
            "border-radius": 4,
            content: "data(name)",
            "text-wrap": "wrap",
            "text-valign": "center",
            "text-halign": "center",
          })
          .selector("edge")
          .css({
            // http://js.cytoscape.org/#style/labels
            label: "data(label)", // maps to data.label
            "text-outline-color": "white",
            "text-outline-width": 3,
            "text-valign": "top",
            "text-halign": "left",
            // https://js.cytoscape.org/demos/edge-types/
            "curve-style": "bezier",
            width: 3,
            "target-arrow-shape": "triangle",
            "line-color": "gray",
            "target-arrow-color": "gray",
          }),
        elements: {
          nodes: nodes,
          edges: edges,
        },
        layout: {
          name: "dagre",
          spacingFactor: 1.5,
          rankDir: "LR",
          fit: true,
        },
      });
      cy.add({
            data: { id: "Z", name: "Z" }
            });
    },
  },
};
</script>
<style lang="scss">
#container {
  height: 600px;
  width: 960px;
}
#cy {
  height: 600px;
  width: 960px;
}
</style>