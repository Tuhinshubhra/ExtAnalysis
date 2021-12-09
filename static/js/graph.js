/**
ExtAnalysis - Browser Extension Analysis Framework
Copyright (C) 2019 - 2022 Tuhinshubhra

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

    var selected_node_label = document.getElementById('selected-node-label');
    var selected_node_group = document.getElementById('selected-node-group');
    var selected_node_parent = document.getElementById('selected-node-parent');
    var selected_node_id = document.getElementById('selected-node-id');
    var currentNode = 'None';
    var currentCid = 'None'
    // create a network
      var container = document.getElementById('large-graph');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        physics: {
            adaptiveTimestep: true,
            barnesHut: {
                gravitationalConstant: -8000,
                springConstant: 0.04,
                springLength: 95
            },
            stabilization: {
                iterations: 987
            }
        },
        layout: {
            randomSeed: 191006,
            improvedLayout: true
        },
        interaction: {
            hideEdgesOnDrag: true,
            tooltipDelay: 200,
            navigationButtons: true,
            keyboard: true
          },
        edges: {
            smooth: {
                type: 'continuous',
                forceDirection: 'horizontal',
                roundness: 0.4
            }
        },
        nodes: {
          size: 20,
                font: {
                    size: 15,
                    color: '#89ff00'
                }
        }, 
          groups: {
              extension: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'extension0.png',
                    selected:imagedir + 'extension1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              html: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'html0.png',
                    selected:imagedir + 'html1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              css: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'css0.png',
                    selected:imagedir + 'css1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              static: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'static0.png',
                    selected:imagedir + 'static1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              js: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'js0.png',
                    selected:imagedir + 'js1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              json: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'json0.png',
                    selected:imagedir + 'json1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              other: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'other0.png',
                    selected:imagedir + 'other1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              directory: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'directory0.png',
                    selected:imagedir + 'directory1.png'
                },
                /** fixed: true,  **/
                /** physics:false **/
              },
              url: {
                shape: 'image',
                image: {
                    unselected:imagedir + 'url0.png',
                    selected:imagedir + 'url1.png'
                },
                /** fixed: true,  **/
                /** physics:false, **/
                /** font: {size:12, color:'blue', face:'sans', background:'white'} **/
              }
          }
      };
      var network = new vis.Network(container, data, options);
      network.on("doubleClick", function(params) {
        if (params.nodes.length == 1) {
            if (network.isCluster(params.nodes[0]) == true) {
                network.openCluster(params.nodes[0]);
            }
        }
    });
      network.on( 'click', function(properties) {
          try {
            var ids = properties.nodes;
            var clickedNodes = nodes.get(ids);
            console.log(clickedNodes);
            var NodeGroup = clickedNodes[0]['group'];
            var NodeLabel = clickedNodes[0]['label'];
            currentNode = clickedNodes[0]['id'];
            currentCid = clickedNodes[0]['cid']

            selected_node_group.innerText = NodeGroup;
            selected_node_label.innerText = NodeLabel;
            selected_node_id.innerText = currentNode;
            selected_node_parent.innerText = currentCid;
          } catch {
              console.log('.');
          }
    });
    $(function() {
		$("#loading").fadeOut("slow");;
    });
    
    function hideSelectedGroup(){
        selected_group = selected_node_group.innerText;
        if (selected_group === 'None'){
            swal("No Node Selected!", "Select a node first! To select a node just click on it.", 'error');
        } else {
            console.log('Hiding Group: ' + selected_group)
        }
    }

    function hideSelectedNode(){
        selected_label = selected_node_label.innerText;
        if (selected_label === 'None'){
            swal("No Node Selected!", "Select a node first! To select a node just click on it.", 'error');
        } else {
            console.log('Hiding label: ' + selected_label)
        }
    }

    function clusterBySelf(selfid=false){
        if (!selfid){
            if (currentCid === 'None' || currentCid === undefined){
                swal("No Node Selected!", "Select a node first! To select a node just click on it.", 'error');
            } else {
                network.setData(data);
                var clusterOptionsByData = {
                    joinCondition:function(childOptions) {
                        return childOptions.cid == currentCid;
                    },
                    clusterNodeProperties: {
                        id:'cidCluster', 
                        shape: 'image',
                        label: 'Cluster of ' + currentCid,
                        image: {
                            unselected:imagedir + 'cluster1.png',
                            selected:imagedir + 'cluster0.png'
                        },
                    }
                };
                network.cluster(clusterOptionsByData);
            }
        } else {
            if (currentNode === 'None'){
                swal("No Node Selected!", "Select a node first! To select a node just click on it.", 'error');
            } else {
                network.setData(data);
                var clusterOptionsByData = {
                    joinCondition:function(childOptions) {
                        return childOptions.cid == currentNode;
                    },
                    clusterNodeProperties: {
                        id:'cidCluster', 
                        shape: 'image',
                        label: 'Cluster of ' + currentNode,
                        image: {
                            unselected:imagedir + 'cluster1.png',
                            selected:imagedir + 'cluster0.png'
                        },
                    }
                };
                network.cluster(clusterOptionsByData);
            }
        }
    }

    function resetGraph(){
        network.setData(data);
    }