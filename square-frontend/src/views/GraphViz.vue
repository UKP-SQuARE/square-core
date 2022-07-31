<template>
  <div class="">
    <h1>Q: A revolving door is convenient for two direction travel, but also serves as a security measure at what?</h1>


    <div class="row">
      <div class="col-auto">
        <div class="row">
          <div class="col-4">
            Num Nodes: {{numShowingNodes}}
          </div>
          <div class="col-8">
            <input type="range" min="1" max="50" v-model="numShowingNodes" class="form-range" id="Range" @change="slider_change()"/>
          </div> 
        </div>

        <div class="row">
          <div class="col-4">
            Spacing Factor: {{spacingFactor}}
          </div>
          <div class="col-8">
          <input type="range" min="0.5" max="2.5" v-model="spacingFactor"  step="0.1" class="form-range" id="SpacingRange" @change="plot_graph()"/>
          </div>
        </div>
      </div>

      <div class="col-auto">
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
      </div>

      <div class="col-auto">
        <!-- Button to restart layout -->
        <button type="button" class="btn btn-outline-primary" @click="restart_layout()">Restart Layout</button>
      </div>

    </div>

    

    <div class="d-flex flex-column justify-content-center">
      <div id="cy" class="cy"></div>
    </div>
      
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
      numShowingNodes: 10,
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
      // if (this.layoutName == "breadthfirst"), add roots = #ans_node
      this.cy.fit();
      this.cy.layout({ 
        name: this.layoutName, //other options: circle, random, grid, breadthfirst
        spacingFactor: this.spacingFactor,
        depthSort: function(a, b){ 
            if (a.data('ans_node')) {
              return 1;
            } else if (b.data('ans_node')) {
              return -1;
            } else {
              if (a.data('q_node')) {
                return -1;
              } else if (b.data('q_node')) {
                return 1;
              } else {
                return 0;
              }
            }
          }
      }).run();
    },
    slider_change(){
      this.get_subgraph(this.numShowingNodes);
      this.plot_graph();
    },
    restart_layout(){
      this.numShowingNodes = 10;
      this.spacingFactor = 1;
      this.layoutName = "breadthfirst";
      this.get_subgraph(this.numShowingNodes);
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
      this.get_subgraph(50);
      this.plot_graph()

      this.slider_change();

  //     this.cy.on('mouseover', 'node', function(event) {
  //     var node = event.cyTarget;
  //     node.qtip({
  //         content: 'hello',
  //         show: {
  //             event: event.type,
  //             // ready: true
  //         },
  //         hide: {
  //             event: 'mouseout unfocus'
  //         }
  //     }, event);
  // });


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
  width: 100%;
  display: block;
}
</style>