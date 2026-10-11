import { useMemo } from "react";
import type { Blueprint, Node } from "./blueprint";

// 좌표는 여기서 계산하므로 데이터에는 위치를 적지 않는다.
// grid: lane = 열, node.row = 행, 화살표로 잇는다.
// tiers: lane = 위아래로 쌓는 가로 띠, node.row = 띠 안의 순서, 띠 사이는 lane.toNext 한 줄로 잇는다.
const LANE_W = 320;
const GAP = 40;
const PAD = 20;
const TOP = 70;
const ROW_GAP = 20;
const BOX_W = LANE_W - 40;
const GROUP_PAD = 8; // 행 사이 틈(ROW_GAP)보다 작아야 위아래 경계 상자가 붙지 않는다

const TIER_W = 1180;
const TIER_LABEL_W = 150;
const TIER_PAD = 14;
const TIER_GROUP_TOP = 24; // 경계 상자 제목이 띠 테두리에 닿지 않게 띠 위쪽을 넓힌다
const TIER_GAP = 16;
const TIER_LINK = 44;
const CARD_MIN_W = 200;

// 글자 폭 추정: 한글·CJK 는 1em, 그 밖은 0.55em.
const textWidth = (text: string, size: number) =>
  [...text].reduce((sum, ch) => sum + (/[ᄀ-ᇿ㄰-㆏가-힯一-鿿]/.test(ch) ? size : size * 0.55), 0);

interface Placed {
  node: Node;
  col: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

interface Band {
  id: string;
  title: string;
  toNext?: string;
  y: number;
  h: number;
}

// 제목 아래 줄 수(lines + tags 한 줄)가 가장 많은 상자에 맞춘다. 태그는 설명 바로 아래에 붙인다.
function boxHeight(blueprint: Blueprint, minLines: number) {
  const shown = (n: Node) => (n.lines?.length ?? 0) + (n.tags?.length ? 1 : 0);
  return 45 + Math.max(minLines, ...blueprint.nodes.map(shown)) * 19;
}

export function layout(blueprint: Blueprint) {
  const col = new Map(blueprint.lanes.map((lane, index) => [lane.id, index]));
  const h = boxHeight(blueprint, 2);
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
    bands: [] as Band[],
    width: PAD * 2 + lanes * LANE_W + Math.max(0, lanes - 1) * GAP,
    height: TOP + rows * (h + ROW_GAP) + 20,
  };
}

export function layoutTiers(blueprint: Blueprint) {
  const h = boxHeight(blueprint, 1);
  const area = TIER_W - PAD * 2 - TIER_LABEL_W - TIER_PAD;
  const maxCols = Math.max(1, Math.floor((area + TIER_GAP) / (CARD_MIN_W + TIER_GAP)));
  const grouped = new Set(blueprint.groups.flatMap((g) => g.nodes));
  const placed = new Map<string, Placed>();
  const bands: Band[] = [];
  let y = PAD;
  blueprint.lanes.forEach((lane, index) => {
    const members = blueprint.nodes.filter((n) => n.lane === lane.id).sort((a, b) => a.row - b.row);
    const cols = Math.max(1, Math.min(members.length, maxCols));
    const w = (area - (cols - 1) * TIER_GAP) / cols;
    const top = members.some((n) => grouped.has(n.id)) ? TIER_GROUP_TOP : TIER_PAD;
    const lines = Math.max(1, Math.ceil(members.length / cols));
    members.forEach((node, at) => {
      const c = at % cols;
      const r = Math.floor(at / cols);
      placed.set(node.id, {
        node,
        col: index,
        x: PAD + TIER_LABEL_W + c * (w + TIER_GAP),
        y: y + top + r * (h + TIER_GAP),
        w,
        h,
      });
    });
    const bandH = top + lines * h + (lines - 1) * TIER_GAP + TIER_PAD;
    bands.push({ id: lane.id, title: lane.title, toNext: lane.toNext, y, h: bandH });
    y += bandH + TIER_LINK;
  });
  return { placed, bands, width: TIER_W, height: y - TIER_LINK + PAD };
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
  const tiers = blueprint.meta.layout === "tiers";
  const { placed, bands, width, height } = useMemo(
    () => (tiers ? layoutTiers(blueprint) : layout(blueprint)),
    [blueprint, tiers],
  );
  const groupPad = tiers ? 6 : GROUP_PAD;
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
        {/* 열은 제목만 둔다. 테두리를 그리면 경계 상자(group)와 선이 겹쳐 도면이 어지럽다. */}
        {!tiers &&
          blueprint.lanes.map((lane, index) => (
            <text key={lane.id} className="lane-title" x={PAD + index * (LANE_W + GAP) + 20} y={38}>
              {lane.title}
            </text>
          ))}
        {bands.map((band, index) => {
          const next = bands[index + 1];
          const cx = PAD + TIER_LABEL_W + (width - PAD * 2 - TIER_LABEL_W - TIER_PAD) / 2;
          const linkTop = band.y + band.h;
          const labelW = band.toNext ? textWidth(band.toNext, 12) + 18 : 0;
          return (
            <g key={band.id}>
              {/* 띠는 상자로 감싸지 않는다. 제목과, 다음 띠 사이의 가는 선 하나로 나눈다. */}
              <text className="band-title" x={PAD} y={band.y + TIER_PAD + 22}>
                {band.title}
              </text>
              {next && (
                <g className="band-link">
                  <path d={`M${PAD} ${linkTop + TIER_LINK / 2}H${width - PAD}`} />
                  {band.toNext && (
                    <>
                      <rect x={cx - labelW / 2} y={linkTop + TIER_LINK / 2 - 10} width={labelW} height={20} />
                      <text x={cx} y={linkTop + TIER_LINK / 2 + 4} textAnchor="middle">
                        {band.toNext}
                      </text>
                    </>
                  )}
                </g>
              )}
            </g>
          );
        })}
        {blueprint.groups.map((group) => {
          const boxes = group.nodes.map((id) => placed.get(id)).filter((p): p is Placed => Boolean(p));
          if (!boxes.length) return null;
          const x = Math.min(...boxes.map((b) => b.x)) - groupPad;
          const y = Math.min(...boxes.map((b) => b.y)) - groupPad;
          const w = Math.max(...boxes.map((b) => b.x + b.w)) + groupPad - x;
          const h = Math.max(...boxes.map((b) => b.y + b.h)) + groupPad - y;
          // 제목은 위 테두리 위에 얹는다. 상자 밖에 두면 위 행과 겹친다.
          return (
            <g key={group.id} className="group">
              <rect className="group-box" x={x} y={y} width={w} height={h} rx={2} />
              <rect className="group-knock" x={x + 8} y={y - 8} width={textWidth(group.title, 13) + 10} height={16} />
              <text className="group-title" x={x + 13} y={y + 4}>
                {group.title}
              </text>
            </g>
          );
        })}
        {!tiers &&
          blueprint.edges.map((edge, index) => {
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
            <text className="node-title" x={x + 16} y={y + 26}>
              {node.title}
            </text>
            {(node.lines || []).map((line, index) => (
              <text key={index} className="sub" x={x + 16} y={y + 48 + index * 19}>
                {line}
              </text>
            ))}
            {node.tags && (
              <text className="tags" x={x + 16} y={y + 48 + (node.lines?.length ?? 0) * 19}>
                {node.tags.join(" · ")}
              </text>
            )}
          </g>
        ))}
      </svg>
    </div>
  );
}
