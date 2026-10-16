/**
 * DeepLearnX Interactive Knowledge Dependency DAG Graph Engine
 * Uses vis-network to render hierarchical concept relationships
 */

let networkInstance = null;
let currentGraphData = null;
let selectedConceptId = null;

const STATUS_DIAGNOSES = {
  mastered: "Concept thoroughly mastered. High transfer to practical application.",
  partial: "Partial understanding. Review conceptual principles and practice numerical derivations.",
  misconception: "Active misconception detected! Flawed mental model in distractor choices.",
  gap: "Critical knowledge gap! Missing foundational prerequisite blocking downstream comprehension.",
  untested: "Concept has not been assessed yet in this evaluation session."
};

async function renderKnowledgeGraph(userId, domain = null) {
  const container = document.getElementById("visNetworkContainer");
  if (!container) return;
  const activeDomain = domain || window.currentDomain || "pokemon";

  try {
    const data = await API.getStudentKnowledgeMap(userId, activeDomain);
    currentGraphData = data;

    const nodesArray = [];
    const edgesArray = [];

    // Construct vis.js Nodes
    (data.graph_nodes || []).forEach(n => {
      const isRoot = n.isRootGap;
      nodesArray.push({
        id: n.id,
        label: `${n.label}\n[${n.sublabel || n.status}]`,
        color: {
          background: n.color || "#64748b",
          border: isRoot ? "#ffffff" : (n.borderColor || "#475569"),
          highlight: {
            background: n.color || "#64748b",
            border: "#ffffff"
          }
        },
        borderWidth: isRoot ? 3 : 1.5,
        shadow: isRoot ? { enabled: true, color: "#ef4444", size: 15 } : false,
        shape: "box",
        margin: 10,
        font: {
          color: n.fontColor || "#ffffff",
          face: "Plus Jakarta Sans",
          size: 13,
          bold: { color: "#ffffff" }
        },
        meta: n
      });
    });

    // Construct vis.js Edges
    (data.graph_edges || []).forEach(e => {
      edgesArray.push({
        from: e.from,
        to: e.to,
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        color: {
          color: e.color || "#64748b",
          highlight: "#6366f1"
        },
        width: e.width || 1.5,
        smooth: { type: "cubicBezier", roundness: 0.2 }
      });
    });

    const visNodes = new vis.DataSet(nodesArray);
    const visEdges = new vis.DataSet(edgesArray);

    const options = {
      layout: {
        hierarchical: {
          direction: "LR", // Left to Right hierarchy: Foundations -> Core -> Advanced
          sortMethod: "directed",
          levelSeparation: 180,
          nodeSpacing: 100
        }
      },
      physics: {
        hierarchicalRepulsion: {
          nodeDistance: 120
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true
      }
    };

    if (networkInstance) {
      networkInstance.destroy();
    }

    networkInstance = new vis.Network(container, { nodes: visNodes, edges: visEdges }, options);

    // Node click handler
    networkInstance.on("click", function(params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        inspectGraphNode(nodeId);
      } else {
        hideNodeInspector();
      }
    });

    // Automatically inspect root gap if detected
    if (data.primary_prerequisite_gap) {
      inspectGraphNode(data.primary_prerequisite_gap);
    }

  } catch (err) {
    console.error("Failed to render knowledge graph:", err);
    container.innerHTML = `<div class="p-4 text-center text-red">Failed to load Knowledge Graph: ${err.message}</div>`;
  }
}

function inspectGraphNode(conceptId) {
  selectedConceptId = conceptId;
  const inspector = document.getElementById("nodeInspectorCard");
  if (!inspector || !currentGraphData) return;

  const nodeInfo = (currentGraphData.graph_nodes || []).find(n => n.id === conceptId);
  if (!nodeInfo) return;

  document.getElementById("inspectNodeTitle").textContent = nodeInfo.label;
  const statusBadge = document.getElementById("inspectNodeStatusBadge");
  statusBadge.textContent = nodeInfo.sublabel || nodeInfo.status;
  statusBadge.className = `badge-tag badge-${getStatusBadgeClass(nodeInfo.status)}`;

  document.getElementById("inspectNodeCategory").textContent = nodeInfo.category || "General";
  document.getElementById("inspectNodeAcc").textContent = (nodeInfo.accuracy !== null && nodeInfo.accuracy !== undefined) ? `${nodeInfo.accuracy}%` : "Untested";
  document.getElementById("inspectNodeDiag").textContent = STATUS_DIAGNOSES[nodeInfo.status] || "No diagnosis available.";

  // Find prerequisites for this concept
  const incoming = (currentGraphData.graph_edges || [])
    .filter(e => e.to === conceptId)
    .map(e => {
      const parent = (currentGraphData.graph_nodes || []).find(n => n.id === e.from);
      return parent ? parent.label : e.from;
    });

  document.getElementById("inspectNodePrereqs").textContent = incoming.length > 0 ? incoming.join(", ") : "None (Foundational Root Node)";
  document.getElementById("inspectNodeDesc").textContent = nodeInfo.meta?.description || `Concept: ${nodeInfo.label}`;

  inspector.classList.remove("hidden");
}

function hideNodeInspector() {
  const inspector = document.getElementById("nodeInspectorCard");
  if (inspector) inspector.classList.add("hidden");
}

function getStatusBadgeClass(status) {
  switch (status) {
    case "mastered": return "emerald";
    case "partial": return "amber";
    case "misconception": return "orange";
    case "gap": return "red";
    default: return "indigo";
  }
}

function launchRemedialForSelectedNode() {
  if (selectedConceptId) {
    openRemedialModal(selectedConceptId);
  }
}
