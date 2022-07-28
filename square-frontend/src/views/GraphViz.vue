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
import graph from './graph_example.json'

// eslint-disable-next-line
const nodes = [
  {
    data: {
      id: "Z",
      name: "QA Node",
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
      id: 'ans',
      name: "German Shephard",
      description: "",
      q_node: false,
      ans_node: true,
      width: 140,
    },
  },
];
// eslint-disable-next-line
const edges = [
  { data: { source: "Z", target: 1, label: "Sub", width: 10 } },
  { data: { source: "Z", target: 2, label: "Sub", width: 20  } },
  { data: { source: 1, target: 3, label: "Sub", width: 30  } },
  { data: { source: 1, target: 4, label: "Sub", width: 40  } },
  { data: { source: 1, target: 5, label: "Sub", width: 50  } },
  { data: { source: 4, target: 6, label: "Sub", width: 60  } },
  { data: { source: 4, target: "ans", label: "Sub", width: 70  } },
];

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
            "color": "white",
          })
          .selector("node[?ans_node]").css({
            "background-color": "#14A07E",
            "color": "white",
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
            // nodes: [
            //   { data: { id: 'ans', name: 'US' } },
            //   { data: { id: 'e', name: 'Obama' } },
            //   { data: { id: 'k', name: 'Trump' } },
            //   { data: { id: 'g', name: 'Biden' } },
            //   { data: { id: 'Z', name: 'QA node', desc: "Q: Who is the US president? Context: The US president ...." } }
            // ],
            // edges: [
            //   { data: { source: 'ans', target: 'e', name: 'president is', weight: 1.0 } },
            //   { data: { source: 'ans', target: 'k', weight: 1.0 } },
            //   { data: { source: 'ans', target: 'g', weight: 1.0 } },
            //   { data: { source: 'e', target: 'ans', name: 'is president of', weight: 1.0} },
            //   { data: { source: 'e', target: 'k', weight: 1.0 } },
            //   { data: { source: 'k', target: 'ans', weight: 1.0 } },
            //   { data: { source: 'k', target: 'e', weight: 1.0 } },
            //   { data: { source: 'k', target: 'g', weight: 1.0 } },
            //   { data: { source: 'g', target: 'ans', weight: 1.0 } },
            //   { data: { source: 'Z', target: 'k', weight: 5.0 } },
            //   { data: { source: 'Z', target: 'e', weight: 5.0 } },
            //   { data: { source: 'Z', target: 'g', weight: 5.0 } },
            // ]
          },
        layout: {
          name: "dagre",
          spacingFactor: 1.5,
          rankDir: "LR",
          fit: true,
        },
      });
      /* eslint-disable */
      var cnt = 0;
      for (const [key, node] of Object.entries(graph["nodes"]["statement_0"])) {
        this.cy.add({
          data: node
        });
        cnt += 1;
        if (cnt == 100) {
          break;
        }
      }
      /* eslint-disable */
      for (const [key, edge] of Object.entries(graph["edges"]["statement_0"])) {
        this.cy.add({
          data: edge
        });
      }




      // this.cy.add({
      //   data: {
      //     id: "QA_node",
      //     name: "QA_node",
      //     description: "",
      //     q_node: false,
      //     ans_node: false,
      //     width: 500,
      //   },
      // });
      // for (const n of nodes){
      //     this.cy.add({
      //       data: n['data']
      //     });
      //     // add edges from Z to question nodes
      //     if (n['data']['q_node']){
      //       this.cy.add({
      //         data: {
      //           source: "QA_node",
      //           target: n['data']['id'],
      //           label: "Sub",
      //           width: 10
      //         }
      //       });
      //     }          
      // }
      // var edges = graph["edges"]["statement_0"]
      for (const e of edges){
          e['data']['opacity'] = e['data']['width']/100;
          this.cy.add({
            data: e['data']
          });
          // add edges from Z to all nodes
      }
      this.cy.layout({ 
          name: 'circle'
        }).run();

      // var dijkstra = this.cy.elements().dijkstra('#QA_node', function(edge){
      //   return edge.data('weight');
      // });
      // var bfs = dijkstra.pathTo(this.cy.$('#7') );
      // // for each node in bfs
      // for (var i = 0; i < bfs.length; i++) {
      //   bfs[i].addClass("highlighted");
      // }
      // console.log(bfs);
      // var x=0;
      // var highlightNextEle = function(bfs){
      //   bfs[x].addClass('highlighted');
      //   if(x<bfs.length){
      //     x++;
      //     setTimeout(highlightNextEle, 500);
      //   }
      // };
      // highlightNextEle(bfs);
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
  width: 960px;
  display: block;
}
</style>