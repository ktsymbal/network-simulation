var network = null;
var currentID = 28;

function destroy() {
  if (network !== null) {
    network.destroy();
    network = null;
  }
}

function sendMessage() {
  if (appConfig.result) {
    $("#message-sending-table").empty()
    $("#message-sending-table-title").text("From " + appConfig.result.source_id + " to " + appConfig.result.target_id)
    $("#message-sending-table").append(
        "<tr><td>" + appConfig.result.path.join("\u2192").substring(0, 60) + "</td>" +
        "<td>" + appConfig.result.service_packets + "</td>" +
        "<td>" + appConfig.result.data_packets + "</td>" +
        "<td>" + appConfig.result.time + "</td></tr>");
        //"<td>" + value.traffic + "</td></tr>");
    $('#message-sending-table-modal').modal('toggle');
  }
}

function init() {
  $.getJSON('/links', function(edges) {
    $.getJSON('/nodes', function(nodes) {
      destroy();

      var data = {
          nodes: nodes,
          edges: edges
      };

      var container = document.getElementById('network');
      var options = {
        width: '1920px',
        height: '960px',
        groups: {
          1: {color:{background:'#82A4CA'}},
          2: {color:{background:'#70C681'}},
          3: {color:{background:'#D5958E'}}
        },
        nodes: {
          shape: 'box',
          borderWidth: 0,
          mass: 30,
          font: {
              size: 20
          },
          shadow: true,
          color: {
            background: '#97C2FC',
          },
        },
        edges: {
          selectionWidth: 2,
          width: 1,
          color: '#3A3534'
        },
        interaction:{
           hover: true,
        },
        physics: false,
        manipulation: {
          initiallyActive: true,
          editEdge: false,
        }
      };
      network = new vis.Network(container, data, options);

      // Handle swithing between duplex and half-duplex by double-click
      network.on("doubleClick", doubleClickHandler);
    });
  });
  sendMessage();
}

function doubleClickHandler(params) {
  // If edge - change edge type
  if (params.edges.length == 1) {
    edge_id = params.edges[0]
    $.getJSON('/link', {'link_id': edge_id}, function(link) {
      if (link) {
        console.log(link);
          var arrows = false;
          if (link.type == "DUPLEX") {
             link.type = "HALF_DUPLEX"
          } else {
            link.type = "DUPLEX"
            arrows = 'to;from'
          }
          network.clustering.updateEdge(edge_id,  {arrows: arrows})
          $.post('update-link', link)
      }
    });
  } else if (params.nodes.length == 1) {
    // If node - get routing table
    node_id = params.nodes[0]
    $.getJSON('/routing-table', {'node_id': node_id}, function(table) {
      if (table) {
          $("#routing-table").empty()
          $("#routing-table-title").text("Routing table for node " + node_id)
          jQuery.each(table, function(index, value) {
            $("#routing-table").append("<tr><td><b>" + index + "</b></td>" +
              "<td>" + value.path.join("\u2192") + "</td>" +
              "<td>" + value.cost + "</td></tr>");
          });
          $('#routing-table-modal').modal('toggle');
      }
    });
  }
}

