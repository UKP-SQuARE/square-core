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
      name: "Q_Node",
      description: "",
      q_node: true,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 1,
      name: "Mammal",
      description: "",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 2,
      name: "Reptile",
      description: "",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 3,
      name: "Horse",
      description: "",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 4,
      name: "Dog",
      description: "Join",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 5,
      name: "Goat",
      description: "Branch Out",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 6,
      name: "Hound",
      description: "",
      q_node: false,
      ans_node: false,
      width: 140,
    },
  },
  {
    data: {
      id: 7,
      name: "German Shephard",
      description: "",
      q_node: false,
      ans_node: true,
      width: 140,
    },
  },
];

const edges = [
  { data: { source: 0, target: 1, label: "Sub", width: 10 } },
  { data: { source: 0, target: 2, label: "Sub", width: 20  } },
  { data: { source: 1, target: 3, label: "Sub", width: 30  } },
  { data: { source: 1, target: 4, label: "Sub", width: 40  } },
  { data: { source: 1, target: 5, label: "Sub", width: 50  } },
  { data: { source: 4, target: 6, label: "Sub", width: 60  } },
  { data: { source: 4, target: 7, label: "Sub", width: 70  } },
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
            "background-color": "white",
            "color": "black",
            "border-color": "gray",
            "border-width": 3,
            "border-radius": 4,
            content: "data(name)",
            "text-wrap": "wrap",
            "text-valign": "center",
            "text-halign": "center",
          })
          .selector("node[?q_node]").css({
            "background-color": "#B238DF",
            "color": "white",
          })
          .selector("node[?ans_node]").css({
            "background-color": "green",
            "color": "white",
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
            "curve-style": "straight-triangle",
            "width": "data(width)",
            "line-color": "#48A7DB",
            "target-arrow-color": "#48A7DB",
            "opacity": "data(opacity)",
          }),
        elements: {
          nodes: [],
          edges: [],
        },
        layout: {
          name: "dagre",
          spacingFactor: 1.5,
          rankDir: "LR",
          fit: true,
        },
      });
      for (const n of nodes){
          cy.add({
            data: n['data']
          });
          // add edges from Z to all nodes
      }
      for (const e of edges){
          e['data']['opacity'] = e['data']['width']/100;
          cy.add({
            data: e['data']
          });
          // add edges from Z to all nodes
      }
      cy.layout({ 
          name: 'circle'
        }).run();
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