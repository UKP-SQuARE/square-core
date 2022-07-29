<template>
  <div class="d-flex flex-column justify-content-center align-items-center">
    <h1>Graph Viz</h1>
    <h4 v-if="loading">Loading</h4>
    <h4 v-if="error" class="text-danger">{{ error }}</h4>
    <button id="path_btn" v-on:click="show_path()"  type="button" class="btn btn-outline-primary">
      Show Question-Answer Path
    </button>
    <div id="cy" class="cy"></div>
  </div>
</template>


<script>
import cydagre from "cytoscape-dagre";
import cytoscape from "cytoscape";
import graph from './graph_sample.json'


export default {
  name: "DataFlow",
  data() {
    return {
      loading: false,
      error: null,
      $cy: null,
    };
  },
  mounted() {
    this.drawGraph();
  },
  methods: {
    show_path() {
      // var fw = this.cy.elements().floydWarshall();
      // fw.path('#Z', '#ans').select();

      // show only the path between the two nodes
      var dijkstra = this.cy.elements().dijkstra('#Z', function(edge){
        return edge.data('weight');
      });
      var bfs = dijkstra.pathTo(this.cy.$('#ans') );
       // for each node in bfs
      for (var i = 0; i < bfs.length; i++) {
        // change node color
        bfs[i].addClass("highlighted");
        // change edge color
        console.log(bfs[i]);
      }


    },
 
    drawGraph() {
      cydagre(cytoscape);
      this.cy= cytoscape({
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
            "color": "black",
          })
          .selector("node[?ans_node]").css({
            "background-color": "#14A07E",
            "color": "black",
          })
          .selector('.highlighted').css({
            'background-color': 'grey',
            'line-color': '#61bffc',
            'target-arrow-color': '#61bffc',
            'transition-property': 'background-color, line-color, target-arrow-color',
            'transition-duration': '0.5s'
          })
          .selector("edge").css({
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
          })
          .selector("edge:selected").css({
            "line-color": "red",
            "target-arrow-color": "red",
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
      /* eslint-disable */
      for (const [key, node] of Object.entries(graph["nodes"]["statement_0"])) {
        this.cy.add({
          data: node
        });

      }
      /* eslint-disable */
      for (const [key, edge] of Object.entries(graph["edges"]["statement_0"])) {
        this.cy.add({
          data: edge
        });
      }

      this.cy.layout({ 
          name: 'breadthfirst' //other options: circle, random, grid, breadthfirst
        }).run();
      },
  },
};
</script>
<style lang="scss">
#container {
  height: 1em;
  width: 960px;
}
#cy {
  height: 600px;
  width: 1600px;
  display: block;
}
</style>