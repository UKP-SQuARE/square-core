<template>
  <div class="modal fade" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" @click.self="close">
    <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click.self="close" />
        </div>
        <div class="modal-body">
          
          <div class="container">
            <div class="text-center">
              <h1>Q: {{this.$store.state.currentQuestion}} </h1>
              <h4>Choices: {{this.$store.state.currentContext}}</h4>
            </div>
            
            <div class="row">
              <div class="col-6">
                <div class="row">
                  <div class="col-5 text-start">
                    Num. Regular Nodes: {{numShowingNodes}}
                  </div>
                  <div class="col-7">
                    <input type="range" min="1" :max="maxNodes" v-model="numShowingNodes" class="form-range" id="Range" @change="slider_change()"/>
                  </div> 
                </div>

                <div class="row">
                  <div class="col-5 text-start">
                    Spacing Factor: {{spacingFactor}}
                  </div>
                  <div class="col-7">
                  <input type="range" min="0.5" max="2.5" v-model="spacingFactor"  step="0.1" class="form-range" id="SpacingRange" @change="plot_graph()"/>
                  </div>
                </div>
                <div class="row">
                  <div class="col-12 text-start">
                    <div class="form-check form-switch">
                      <input class="form-check-input" type="checkbox" role="switch" id="showHideEdgeLabels" v-model="showEdgeLabelsFlag" @change="showEdgeLabels()">
                      <label class="form-check-label" for="showHideEdgeLabels" id="lbl_showHideEdgeLabels">Show edge labels</label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-4">
                <div class="row">
                  <div class="col-2">
                    <br>Layout:
                  </div>
                  <div class="col-10">
                    <div class="form-check">
                      <input class="form-check-input" type="radio" id="dagre" value="dagre" v-model="layoutName" @change="plot_graph()"/>
                      <label class="form-check-label" for="dagre">dagre</label>
                    </div>
                    <div class="form-check">
                      <input class="form-check-input" type="radio" id="breadthfirst" value="breadthfirst" v-model="layoutName" @change="plot_graph()"/>
                      <label class="form-check-label" for="breadthfirst">Breadth First</label>
                    </div>
                    <div class="form-check">
                      <input class="form-check-input" type="radio" id="grid" value="grid" v-model="layoutName" @change="plot_graph()"/>
                      <label class="form-check-label" for="grid">Grid</label>
                    </div>  
                  </div>
                </div> <!-- end row -->
              </div> <!-- end col -->


              <div class="col-2">
                <div class="d-grid gap-2">
                  <button type="button" class="btn btn-outline-primary" @click="lm_graph()" >LM Graph</button>
                  <button type="button" class="btn btn-outline-primary" @click="attn_graph()" >Attention Graph</button>
                  <button type="button" class="btn btn-outline-primary" @click="resetZoom()" >Reset Zoom</button>
                </div>
              </div>
              <!-- <div class="col-auto">
                <button type="button" class="btn btn-outline-primary" @click="restart_layout()">Restart Layout</button>
              </div> -->
              

            </div> <!-- end row -->
          </div> <!-- end container text-center -->

          <div class="d-flex flex-column justify-content-center">
            <div id="cy" class="cy"></div>
          </div>
          <div>
            <p>Legend: Question nodes in <font color="#B238DF">purple</font>, answer nodes in <font color="#14A07E">green</font>.
            Clicking on a node or edge will hide it.</p>
          </div>

        </div>  <!-- end modal-body -->
      </div>  <!-- end modal-content -->
    </div>  <!-- end modal-dialog -->
  </div>  <!-- end modal -->

</template>

<script>
import cydagre from "cytoscape-dagre";
import cytoscape from "cytoscape";
import popper from 'cytoscape-popper';


export default {
  name: "DataFlow",
  data() {
    return {
      loading: false,
      error: null,
      $cy: null,
      lm_subgraph: this.$store.state.currentResults[0].predictions[0].prediction_graph['lm_subgraph'],
      attn_subgraph: this.$store.state.currentResults[0].predictions[0].prediction_graph['attn_subgraph'],
      maxNodes: 50,
      numShowingNodes: 5,
      spacingFactor: 1,
      layoutName: "breadthfirst",
      showEdgeLabelsFlag: false,
    };
  },
  mounted() {
    cytoscape.use( popper );
    cytoscape.use( cydagre );
    this.init_cytoscape();
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
      this.cy.layout({ 
        name: this.layoutName, //other options: circle, random, grid, breadthfirst
        circle: true,
        padding: 0,
        root: '[q_node = true]',
        spacingFactor: this.spacingFactor,
        // depthSort: function(a, b){ 
        //     if (a.data('ans_node')) {
        //       return 1;
        //     } else if (b.data('ans_node')) {
        //       return -1;
        //     } else {
        //       if (a.data('q_node')) {
        //         return -1;
        //       } else if (b.data('q_node')) {
        //         return 1;
        //       } else {
        //         return 0;
        //       }
        //     }
        //   }
      }).run();
      this.cy.fit();
    },
    resetZoom() {
      this.cy.fit();
    },
    showEdgeLabels(){
      this.cy.edges().toggleClass("showlabel");
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
    lm_graph(){
      this.showEdgeLabelsFlag = false;
      this.lm_subgraph = this.$store.state.currentResults[0].predictions[0].prediction_graph['lm_subgraph'];
      this.cy.elements().remove();
      var cnt = 0;
      /* eslint-disable */
      for (const [key, node] of Object.entries(this.lm_subgraph["nodes"])) {
        node['lbl_width'] = node['name'].length * 10; //
        // node['opacity'] = node['width']/100;
        node['rank'] = cnt;
        // replace "_" with " " in the node name  to make it readable
        node['name'] = node['name'].replace(/_/g, " ");
        cnt += 1;
        this.cy.add({
          data: node
        });

      }
      /* eslint-disable */
      for (const [key, edge] of Object.entries(this.lm_subgraph["edges"])) {
        edge['opacity'] = edge['weight'];
        // edge['width'] = edge['weight'] * 10;
        // replace "_" with " " in the edge label  to make it readable
        edge['label'] = edge['label'].replace(/_/g, " ");
        // if inverse edge is not in the graph, add it
        let inv_edges = this.cy.filter(function(element, i){
          return element.isEdge() && element.data('source') == edge['target'] && element.data('target') == edge['source'] && element.data('label') == edge['label'];
        });
        if (!this.self_loop(edge) && inv_edges.length == 0) {
          this.cy.add({
            data: edge
          });
        }
      }
      this.maxNodes = 50;
      this.get_subgraph(this.maxNodes);
      this.slider_change();
      this.plot_graph();
    },
    attn_graph(){
      this.showEdgeLabelsFlag = false;
      this.attn_subgraph = this.$store.state.currentResults[0].predictions[0].prediction_graph['attn_subgraph'];
      this.cy.elements().remove();
      var cnt = 0
      /* eslint-disable */
      for (const [key, node] of Object.entries(this.attn_subgraph["nodes"])) {
        node['lbl_width'] = node['name'].length * 10;
        // node['opacity'] = node['width']/100;
        node['rank'] = cnt;
        // replace "_" with " " in the node name  to make it readable
        node['name'] = node['name'].replace(/_/g, " ");
        cnt += 1;
        this.cy.add({
          data: node
        });

      }
      /* eslint-disable */
      for (const [key, edge] of Object.entries(this.attn_subgraph["edges"])) {
        // edge['opacity'] = edge['weight'];
        // edge['width'] = edge['weight'] * 10;
        // replace "_" with " " in the edge label  to make it readable
        edge['label'] = edge['label'].replace(/_/g, " ");
        // if inverse edge is not in the graph, add it
        let inv_edges = this.cy.filter(function(element, i){
          return element.isEdge() && element.data('source') == edge['target'] && element.data('target') == edge['source'] && element.data('label') == edge['label'];
        });
        if (!this.self_loop(edge) && inv_edges.length == 0) {
          this.cy.add({
            data: edge
          });
        }
      this.maxNodes = Math.min(this.maxNodes, this.cy.nodes().length);
      this.numShowingNodes = this.maxNodes
      this.get_subgraph(this.numShowingNodes);
      this.slider_change();
      this.plot_graph();
      }
    },
    self_loop(edge){
      return edge['source'] == edge['target'];
    },
    init_cytoscape() {
      cydagre(cytoscape);
      this.cy= cytoscape({
        container: document.getElementById("cy"),
        boxSelectionEnabled: false,
        autounselectify: true,
        style: cytoscape
          .stylesheet()
          .selector("node")
          .css({
            "shape": "roundrectangle",
            "text-wrap": "wrap",
            "width": "data(lbl_width)",
            // "opacity": "data(opacity)",
            "background-color": "white",
            "color": "black",
            "border-color": "gray",
            "border-width": 3,
            "border-radius": 4,
            "content": "data(name)",
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
            // label: "data(label)", // maps to data.label
            "text-outline-color": "white",
            // "text-outline-width": "10px",
            // "font-size": "50px",
            "text-valign": "top",
            "text-halign": "left",
            // https://js.cytoscape.org/demos/edge-types/
            "curve-style": "bezier", //"straight-triangle",
            // "width": "data(width)",
            // "opacity": "data(opacity)",
            "line-color": "#48A7DB",
            "target-arrow-color": "#48A7DB",
          })
          .selector("edge.showlabel").css({
            "label": "data(label)", // maps to data.label
          }),
          elements: {
            nodes: [],
            edges: [],
          },
      });

      this.cy.on('tap', 'node', function (evt) {
        // hide node
        evt.target.addClass("hidden");
      });
      this.cy.on('tap', 'edge', function (evt) {
        // hide edge
        evt.target.addClass("hidden");
      });
      // when hover on edge, show edge label
      this.cy.elements().unbind("mouseover");
      this.cy.elements().bind("mouseover", (event) => {
        event.target.popperRefObj = event.target.popper({
          content: () => {
            let content = document.createElement("div");

            content.classList.add("popper-div");

            content.innerHTML = event.target.width().toFixed(2);;

            document.body.appendChild(content);
            return content;
          },
        });
      });
      this.cy.elements().unbind("mouseout");
      this.cy.elements().bind("mouseout", (event) => {
        if (event.target.popper) {
          event.target.popperRefObj.state.elements.popper.remove();
          event.target.popperRefObj.destroy();
        }
      });

    },
    close(){
      this.cy.elements().remove();
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