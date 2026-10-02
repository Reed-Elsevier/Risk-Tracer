"use client";

import { useEffect, useMemo } from "react";
import { Background, Controls, Handle, MarkerType, Position, ReactFlow, useNodesInitialized, useReactFlow } from "@xyflow/react";
import type { Edge, Node, NodeProps } from "@xyflow/react";
import { ArrowRight, Building2, Landmark, ShieldAlert } from "lucide-react";
import "@xyflow/react/dist/style.css";

import type { Investigation } from "@/lib/types";

type GraphNode = Investigation["graph"]["nodes"][number];
type OwnershipFlowNode = Node<GraphNode, "ownership">;

const nodeTypes = { ownership: OwnershipNode };

function FitOwnershipPath() {
  const nodesInitialized = useNodesInitialized();
  const { fitView } = useReactFlow();

  useEffect(() => {
    if (nodesInitialized) {
      void fitView({ padding: 0.22, minZoom: 0.16, maxZoom: 1 });
    }
  }, [fitView, nodesInitialized]);

  return null;
}

function OwnershipNode({ data }: NodeProps<OwnershipFlowNode>) {
  const isSupplier = data.kind === "supplier_entity";
  const Icon = data.listed ? ShieldAlert : isSupplier ? Building2 : Landmark;
  const role = data.listed ? "Listed entity" : isSupplier ? "Supplier" : "Upstream entity";

  return (
    <div className={`flow-node ${isSupplier ? "supplier" : ""} ${data.listed ? "listed" : ""}`}>
      <Handle type="target" position={Position.Left} className="flow-handle" />
      <div className="flow-node__header">
        <span className="flow-node__icon" aria-hidden="true"><Icon size={15} strokeWidth={2} /></span>
        <span className="flow-node__role">{role}</span>
      </div>
      <div className="flow-node__name">{data.label}</div>
      <div className="flow-node__id">{data.entity_id}</div>
      {data.watchlist_entry_id && (
        <div className="flow-node__watchlist">
          <ShieldAlert size={12} aria-hidden="true" />
          <span>{data.watchlist_entry_id}</span>
        </div>
      )}
      <Handle type="source" position={Position.Right} className="flow-handle" />
    </div>
  );
}

function layoutNodes(graph: Investigation["graph"]): OwnershipFlowNode[] {
  const incoming = new Map(graph.nodes.map((node) => [node.id, 0]));
  const outgoing = new Map<string, string[]>();
  const levels = new Map(graph.nodes.map((node) => [node.id, 0]));

  graph.edges.forEach((edge) => {
    incoming.set(edge.target, (incoming.get(edge.target) ?? 0) + 1);
    outgoing.set(edge.source, [...(outgoing.get(edge.source) ?? []), edge.target]);
  });

  const queue = graph.nodes.filter((node) => incoming.get(node.id) === 0).map((node) => node.id);
  for (let index = 0; index < queue.length; index += 1) {
    const source = queue[index];
    for (const target of outgoing.get(source) ?? []) {
      levels.set(target, Math.max(levels.get(target) ?? 0, (levels.get(source) ?? 0) + 1));
      incoming.set(target, (incoming.get(target) ?? 1) - 1);
      if (incoming.get(target) === 0) queue.push(target);
    }
  }

  const columns = new Map<number, GraphNode[]>();
  graph.nodes.forEach((node) => {
    const level = levels.get(node.id) ?? 0;
    columns.set(level, [...(columns.get(level) ?? []), node]);
  });

  return [...columns.entries()].flatMap(([level, nodes]) =>
    nodes.map((node, index) => ({
      id: node.id,
      type: "ownership",
      position: { x: level * 380, y: index * 180 },
      data: node,
      draggable: false,
      selectable: false,
    }))
  );
}

export default function OwnershipGraph({ graph }: { graph: Investigation["graph"] }) {
  const entityNames = useMemo(
    () => new Map(graph.nodes.map((node) => [node.id, node.label])),
    [graph.nodes]
  );
  const nodes = useMemo<Node[]>(
    () => layoutNodes(graph),
    [graph]
  );
  const edges = useMemo<Edge[]>(
    () => graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label.split(" · ")[0],
      type: "smoothstep",
      markerEnd: { type: MarkerType.ArrowClosed, color: "#1e4e8c", width: 18, height: 18 },
      style: { stroke: "#1e4e8c", strokeWidth: 1.75 },
      labelStyle: { fill: "#1e4e8c", fontSize: 11, fontWeight: 600 },
      labelShowBg: true,
      labelBgStyle: { fill: "#ffffff", fillOpacity: 0.96, stroke: "#cbd8e8", strokeWidth: 1 },
      labelBgPadding: [8, 5],
      labelBgBorderRadius: 7,
    })),
    [graph.edges]
  );

  return (
    <section id="ownership-path" className="rounded-2xl border border-black/15 bg-white p-5 shadow-card">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-ink">Recorded ownership path</h2>
          <p className="mt-1 max-w-2xl text-sm text-black/60">Up to two upstream links are shown. Follow the arrows from parent entity to supplier.</p>
        </div>
        <div className="flex flex-wrap gap-2 text-[11px] font-semibold text-black/70" aria-label="Graph legend">
          <span className="graph-legend graph-legend--supplier">Supplier</span>
          <span className="graph-legend graph-legend--upstream">Upstream</span>
          <span className="graph-legend graph-legend--listed">Listed</span>
        </div>
      </div>
      <div className="ownership-canvas h-[500px] overflow-hidden rounded-xl border border-black/10 sm:h-[460px]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.22, minZoom: 0.16, maxZoom: 1 }}
          minZoom={0.15}
          maxZoom={1.5}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          proOptions={{ hideAttribution: true }}
          aria-label="Recorded ownership path"
        >
          <FitOwnershipPath />
          <Background color="#cbd8e8" gap={24} size={1} />
          <Controls showInteractive={false} position="bottom-right" />
        </ReactFlow>
      </div>
      <div className="mt-6 border-t border-black/10 pt-5">
        <h3 className="text-base font-bold tracking-tight text-ink">Relationship details</h3>
        <p className="mt-1 text-sm text-black/60">Complete relationship type, ownership share, date, and source record.</p>
        <ol className="mt-4 divide-y divide-black/10 border-y border-black/10">
          {graph.edges.map((edge) => {
            const [relationship = "Recorded", share = "Not recorded", effectiveDate = "Date not recorded"] = edge.label.split(" · ");
            return (
              <li key={edge.id} className="grid gap-3 py-4 sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center sm:gap-6">
                <div className="min-w-0">
                  <div className="grid min-w-0 grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-start gap-2 text-sm font-semibold text-black">
                    <span className="break-words">{entityNames.get(edge.source) ?? edge.source}</span>
                    <ArrowRight size={15} className="mt-0.5 shrink-0 text-[#1e4e8c]" aria-hidden="true" />
                    <span className="break-words">{entityNames.get(edge.target) ?? edge.target}</span>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                    <span className="rounded-md bg-[#1e4e8c] px-2 py-1 font-semibold text-white">{relationship}</span>
                    <span className="font-mono font-semibold text-[#1e4e8c]">{edge.ownership_link_id}</span>
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-black/55">Ownership</p>
                  <p className="mt-1 text-sm font-semibold text-black">{share}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-black/55">Effective</p>
                  <p className="mt-1 font-mono text-xs font-semibold text-black">{effectiveDate}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
