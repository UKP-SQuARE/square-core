<template>
  <div class="d-flex flex-column justify-content-center align-items-center">
    <h1>A revolving door is convenient for two direction travel, but also serves as a security measure at what?</h1>
    <h4 v-if="loading">Loading</h4>
    <h4 v-if="error" class="text-danger">{{ error }}</h4>
    <!-- <button id="path_btn" v-on:click="show_path()"  type="button" class="btn btn-outline-primary">
      Show Question-Answer Path
    </button> -->
    <div class="col-6">
      Num Nodes: <input type="range" min="1" max="50" value="10" class="form-range" id="Range" @change="slider_change()" oninput="this.nextElementSibling.value = this.value" >
      <output/>
    </div>
    <div class="col-6">
      Spacing Factor: <input type="range" min="0.5" max="2.5" v-model="spacingFactor"  step="0.1" class="form-range" id="SpacingRange" @change="spacingSliderChange()"/>
    </div>

    <div class="col-auto">
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" id="circle" value="circle" v-model="layoutName" @change="plot_graph()"/>
        <label class="form-check-label" for="circle">circle</label>
      </div>
      
    </div>
    <div class="col-auto">
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" id="breadthfirst" value="breadthfirst" v-model="layoutName" @change="plot_graph()"/>
        <label class="form-check-label" for="breadthfirst">breadthfirst</label>
      </div>
        
    </div>
    <div class="col-auto">
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" id="grid" value="grid" v-model="layoutName" @change="plot_graph()"/>
        <label class="form-check-label" for="grid">grid</label>
      </div>  
    </div>
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
      spacingFactor: 1,
      layoutName: "breadthfirst"
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
    get_subgraph(num_nodes){
      this.cy.nodes().addClass("hidden");
      // eslint-disable-next-line
      var subgraph = this.cy.filter(function(element, i){
        return element.isNode() && (element.data('q_node') == true || element.data('ans_node') == true || element.data('rank') < num_nodes);
      });
      subgraph.removeClass("hidden");
      return subgraph;

      
    },
    plot_graph() {
      this.cy.fit();
      this.cy.layout({ 
        name: this.layoutName, //other options: circle, random, grid, breadthfirst
        spacingFactor: this.spacingFactor,
      }).run();
    
    },
    slider_change(){
      var num_nodes = document.getElementById("Range").value;
      this.get_subgraph(num_nodes);
      this.plot_graph();
    },
    spacingSliderChange(){
      this.plot_graph();
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
            "shape": "hexagon"
          })
          .selector('.highlighted').css({
            'background-color': 'grey',
            'line-color': '#61bffc',
            'target-arrow-color': '#61bffc',
            'transition-property': 'background-color, line-color, target-arrow-color',
            'transition-duration': '0.5s'
          })
          .selector('.hidden').css({
            'display': 'none'
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
      var cnt = 0
      for (const [key, node] of Object.entries(graph["nodes"]["statement_0"])) {
        node['rank'] = cnt;
        cnt += 1;
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
      // get full graph
      var subgraph = this.get_subgraph(50);
      // remove class hidden from the subgraph
      subgraph.removeClass("hidden");
      this.plot_graph()

      this.slider_change();


      // // .addClass("hidden") to all nodes
      // this.cy.nodes().addClass("hidden");
      // // get the subgraph of the top k nodes
      // var subgraph = this.get_subgraph(50);
      // // remove class hidden from the subgraph
      // subgraph.removeClass("hidden");
      // // plot the subgraph 
      // this.cy.layout({ 
      //     name: 'breadthfirst' //other options: circle, random, grid, breadthfirst
      //   }).run();


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