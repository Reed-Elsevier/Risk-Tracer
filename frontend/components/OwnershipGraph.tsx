"use client";

import { useMemo } from "react";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import type { Edge, Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { Investigation } from "@/lib/types";

export default function OwnershipGraph({ graph }: { graph: Investigation["graph"] }) {
  const nodes = useMemo<Node[]>(
    () => graph.nodes.map((node, index) => ({
      id: node.id,
      position: { x: (index % 3) * 260, y: Math.floor(index / 3) * 150 },
      data: { label: <div className={`flow-node ${node.kind === "supplier_entity" ? "supplier" : ""} ${node.listed ? "listed" : ""}`}><div className="text-[10px] font-bold uppercase tracking-widest text-black/60">{node.kind.replace("_", " ")}</div><div className="mt-1 font-semibold text-ink">{node.label}</div><div className="mt-1 font-mono text-[10px] text-black/60">{node.entity_id}</div>{node.watchlist_entry_id && <div className="mt-2 text-[10px] font-semibold text-[#1e4e8c]">{node.watchlist_entry_id}</div>}</div> },
      style: { background: "transparent", border: "none", padding: 0, width: 190 }
    })),
    [graph.nodes]
  );
  const edges = useMemo<Edge[]>(
    () => graph.edges.map((edge) => ({ id: edge.id, source: edge.source, target: edge.target, label: edge.label, type: "smoothstep", animated: false, style: { stroke: "#1e4e8c" }, labelStyle: { fill: "#1e4e8c" } })),
    [graph.edges]
  );

  return (
    <section className="rounded-2xl border border-black/15 bg-white p-5 shadow-card">
      <div className="mb-4">
        <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-black/60">Ownership graph</p>
        <h2 className="text-xl font-semibold tracking-tight text-ink">Recorded entity links</h2>
        <p className="mt-1 text-sm text-black/60">At most two upstream links are shown. Arrows follow the recorded parent → child direction.</p>
      </div>
      <div className="h-[420px] overflow-hidden rounded-xl border border-black/10 bg-white">
        <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.22 }} nodesDraggable={false} nodesConnectable={false} proOptions={{ hideAttribution: true }}>
          <Background color="#e6e6e6" gap={24} />
          <Controls />
          <MiniMap pannable zoomable />
        </ReactFlow>
      </div>
    </section>
  );
}
