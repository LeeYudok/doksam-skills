import { useMemo } from "react";
import type { Blueprint, Node } from "./blueprint";

// lane = 열, node.row = 행. 좌표는 여기서 계산하므로 데이터에는 위치를 적지 않는다.
const LANE_W = 320;
const GAP = 40;
const PAD = 20;
const TOP = 70;
const ROW_GAP = 20;
const BOX_W = LANE_W - 40;

interface Placed {
  node: Node;
  col: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

export function layout(blueprint: Blueprint) {
  const col = new Map(blueprint.lanes.map((lane, index) => [lane.id, index]));
  const maxLines = Math.max(2, ...blueprint.nodes.map((n) => n.lines?.length ?? 0));
  const h = 52 + maxLines * 19;
  const rows = Math.max(0, ...blueprint.nodes.map((n) => n.row)) + 1;
  const placed = new Map<string, Placed>();
  for (const node of blueprint.nodes) {
    const c = col.get(node.lane) ?? 0;
    placed.set(node.id, {
      node,
      col: c,
      x: PAD + c * (LANE_W + GAP) + 20,
      y: TOP + node.row * (h + ROW_GAP),
      w: BOX_W,
      h,
    });
  }
  const lanes = blueprint.lanes.length;
  return {
    placed,
    width: PAD * 2 + lanes * LANE_W + Math.max(0, lanes - 1) * GAP,
    height: TOP + rows * (h + ROW_GAP) + 20,
  };
}

function edgeGeometry(a: Placed, b: Placed) {
  if (a.col === b.col) {
    const x = a.x + a.w / 2;
    const down = a.y < b.y;
    const from = down ? a.y + a.h : a.y;
    const to = down ? b.y : b.y + b.h;
    return { d: `M${x} ${from}V${to}`, lx: x + 8, ly: (from + to) / 2 + 4, anchor: "start" };
  }
  const right = b.col > a.col;
  const sx = right ? a.x + a.w : a.x;
  const ex = right ? b.x : b.x + b.w;
  const sy = a.y + a.h / 2;
  const ey = b.y + b.h / 2;
  if (sy === ey)
    return { d: `M${sx} ${sy}H${ex}`, lx: (sx + ex) / 2, ly: sy - 8, anchor: "middle" };
  // 곁 열 사이 틈의 가운데에서 꺾는다. 열을 건너뛰는 선은 사이 상자를 지날 수 있으니 행을 비켜 둔다.
  const mx = sx + (right ? 40 : -40);
  return {
    d: `M${sx} ${sy}H${mx}V${ey}H${ex}`,
    lx: mx,
    ly: Math.min(sy, ey) - 8,
    anchor: "middle",
  };
}

export function Diagram({
  blueprint,
  selected,
  dimmed,
  onSelect,
}: {
  blueprint: Blueprint;
  selected: string;
  dimmed: Set<string>;
  onSelect: (id: string) => void;
}) {
  const { placed, width, height } = useMemo(() => layout(blueprint), [blueprint]);
  return (
    <div className="diagram-wrap">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ minWidth: Math.min(width, 900) }}
        role="group"
        aria-label="구성도"
      >
        <defs>
          <marker id="bp-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M0 0L10 5L0 10Z" className="arrow-head" />
          </marker>
        </defs>
        {blueprint.lanes.map((lane, index) => {
          const x = PAD + index * (LANE_W + GAP);
          return (
            <g key={lane.id}>
              <rect className="lane" x={x} y={50} width={LANE_W} height={height - 70} rx={2} />
              <text className="lane-title" x={x + 20} y={38}>
                {lane.title}
              </text>
            </g>
          );
        })}
        {blueprint.edges.map((edge, index) => {
          const from = placed.get(edge.from);
          const to = placed.get(edge.to);
          if (!from || !to) return null;
          const g = edgeGeometry(from, to);
          return (
            <g key={`${edge.from}-${edge.to}-${index}`} className={`edge ${edge.type || "flow"}`}>
              <path d={g.d} markerEnd="url(#bp-arrow)" />
              {edge.label && (
                <text x={g.lx} y={g.ly} textAnchor={g.anchor as "start" | "middle"}>
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}
        {[...placed.values()].map(({ node, x, y, w, h }) => (
          <g
            key={node.id}
            id={`node-${node.id}`}
            className={`node state-${node.state}${selected === node.id ? " selected" : ""}${dimmed.has(node.id) ? " dim" : ""}`}
            role="button"
            tabIndex={0}
            aria-pressed={selected === node.id}
            aria-label={`${node.title}: ${node.summary}`}
            onClick={() => onSelect(node.id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(node.id);
              }
            }}
          >
            <rect className="box" x={x} y={y} width={w} height={h} rx={2} />
            <path className="stripe" d={`M${x} ${y}V${y + h}`} />
            <text className="node-title" x={x + 16} y={y + 26}>
              {node.title}
            </text>
            {(node.lines || []).map((line, index) => (
              <text key={index} className="sub" x={x + 16} y={y + 48 + index * 19}>
                {line}
              </text>
            ))}
          </g>
        ))}
      </svg>
    </div>
  );
}
