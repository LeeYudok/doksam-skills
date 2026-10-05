// 청사진 데이터(JSONL) 스키마와 파서. 화면(Vite)과 검사기(sh scripts/check.sh)가 같은 코드를 쓴다.
// 파일 순서 = 표시 순서. 줄마다 JSON 한 개, kind 로 종류를 구분한다.

export type State = "done" | "partial" | "missing";
export type Priority = "P0" | "P1" | "P2";

export interface Meta {
  kind: "meta";
  title: string;
  eyebrow?: string;
  summary?: string;
  badges?: string[];
  links?: { label: string; href: string }[];
  asOf: string;
}
export interface Lane {
  kind: "lane";
  id: string;
  title: string;
}
export interface Node {
  kind: "node";
  id: string;
  lane: string;
  row: number;
  title: string;
  lines?: string[];
  state: State;
  summary: string;
  paths?: string[];
  next?: string;
  gap?: string;
}
export interface Edge {
  kind: "edge";
  from: string;
  to: string;
  label?: string;
  type?: "flow" | "write";
}
export interface Step {
  kind: "flow";
  title: string;
  body: string;
}
export interface Feature {
  kind: "feature";
  name: string;
  state: State;
  now: string;
  remaining: string;
}
export interface Gap {
  kind: "gap";
  id: string;
  priority: Priority;
  title: string;
  state: State;
  now: string;
  todo: string;
  done: string;
  paths?: string[];
}
export interface Doc {
  kind: "doc";
  id: string;
  title: string;
  paragraphs: string[];
}
export interface Blueprint {
  meta: Meta;
  lanes: Lane[];
  nodes: Node[];
  edges: Edge[];
  flow: Step[];
  features: Feature[];
  gaps: Gap[];
  docs: Doc[];
}
export interface Parsed {
  blueprint: Blueprint | null;
  errors: string[];
}
export interface Source {
  name: string;
  text: string;
}

type Field = { t: "s" | "i" | "a" | "e" | "l"; opt: boolean; values?: readonly string[] };
const s = (opt = false): Field => ({ t: "s", opt });
const i = (): Field => ({ t: "i", opt: false });
const a = (opt = false): Field => ({ t: "a", opt });
const l = (opt = false): Field => ({ t: "l", opt });
const e = (values: readonly string[], opt = false): Field => ({
  t: "e",
  opt,
  values,
});
const STATES = ["done", "partial", "missing"] as const;

const SPECS: Record<string, Record<string, Field>> = {
  meta: { title: s(), eyebrow: s(true), summary: s(true), badges: a(true), links: l(true), asOf: s() },
  lane: { id: s(), title: s() },
  node: {
    id: s(),
    lane: s(),
    row: i(),
    title: s(),
    lines: a(true),
    state: e(STATES),
    summary: s(),
    paths: a(true),
    next: s(true),
    gap: s(true),
  },
  edge: { from: s(), to: s(), label: s(true), type: e(["flow", "write"], true) },
  flow: { title: s(), body: s() },
  feature: { name: s(), state: e(STATES), now: s(), remaining: s() },
  gap: {
    id: s(),
    priority: e(["P0", "P1", "P2"]),
    title: s(),
    state: e(STATES),
    now: s(),
    todo: s(),
    done: s(),
    paths: a(true),
  },
  doc: { id: s(), title: s(), paragraphs: a() },
};

function checkField(key: string, value: unknown, field: Field): string | null {
  if (value === undefined) return field.opt ? null : `'${key}' 가 없습니다`;
  if (field.t === "s")
    return typeof value === "string" && value.trim()
      ? null
      : `'${key}' 는 비어 있지 않은 문자열이어야 합니다`;
  if (field.t === "i")
    return Number.isInteger(value) && (value as number) >= 0
      ? null
      : `'${key}' 는 0 이상의 정수여야 합니다`;
  if (field.t === "a")
    return Array.isArray(value) &&
      value.length > 0 &&
      value.every((item) => typeof item === "string" && item.trim())
      ? null
      : `'${key}' 는 비어 있지 않은 문자열 배열이어야 합니다`;
  if (field.t === "l")
    return Array.isArray(value) &&
      value.length > 0 &&
      value.every(
        (item) =>
          typeof item === "object" &&
          item !== null &&
          typeof item.label === "string" &&
          item.label.trim() &&
          typeof item.href === "string" &&
          /^(\/|#|https?:\/\/)/.test(item.href),
      )
      ? null
      : `'${key}' 는 {label, href} 배열이어야 하고 href 는 / # http(s):// 로 시작해야 합니다`;
  return typeof value === "string" && field.values?.includes(value)
    ? null
    : `'${key}' 는 ${field.values?.join("·")} 중 하나여야 합니다`;
}

function validate(kind: string, obj: Record<string, unknown>): string[] {
  const spec = SPECS[kind];
  const problems: string[] = [];
  for (const key of Object.keys(obj))
    if (key !== "kind" && !(key in spec))
      problems.push(`알 수 없는 필드 '${key}' (${kind})`);
  for (const [key, field] of Object.entries(spec)) {
    const problem = checkField(key, obj[key], field);
    if (problem) problems.push(`${problem} (${kind})`);
  }
  return problems;
}

function duplicates(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

export function parseBlueprint(sources: Source[]): Parsed {
  const errors: string[] = [];
  const records: { at: string; value: Record<string, unknown> & { kind: string } }[] = [];
  for (const source of [...sources].sort((x, y) => x.name.localeCompare(y.name))) {
    source.text.split("\n").forEach((line, index) => {
      if (!line.trim()) return;
      const at = `${source.name}:${index + 1}`;
      let value: unknown;
      try {
        value = JSON.parse(line);
      } catch (error) {
        errors.push(`${at}: JSON 문법 오류 — ${(error as Error).message}`);
        return;
      }
      if (typeof value !== "object" || value === null || Array.isArray(value)) {
        errors.push(`${at}: 한 줄은 JSON 객체 하나여야 합니다`);
        return;
      }
      const record = value as Record<string, unknown>;
      const kind = typeof record.kind === "string" ? record.kind : "";
      if (!(kind in SPECS)) {
        errors.push(`${at}: kind 는 ${Object.keys(SPECS).join("·")} 중 하나여야 합니다`);
        return;
      }
      const problems = validate(kind, record);
      for (const problem of problems) errors.push(`${at}: ${problem}`);
      if (!problems.length) records.push({ at, value: record as never });
    });
  }
  const of = <T,>(kind: string) =>
    records.filter((r) => r.value.kind === kind).map((r) => r.value as unknown as T);
  const metas = of<Meta>("meta");
  const lanes = of<Lane>("lane");
  const nodes = of<Node>("node");
  const edges = of<Edge>("edge");
  const gaps = of<Gap>("gap");
  const docs = of<Doc>("doc");
  if (metas.length !== 1) errors.push(`meta 줄은 정확히 하나여야 합니다 (현재 ${metas.length}개)`);
  else if (
    !/^\d{4}-\d{2}-\d{2}$/.test(metas[0].asOf) ||
    Number.isNaN(Date.parse(metas[0].asOf))
  )
    errors.push(`meta.asOf 는 실제 날짜 YYYY-MM-DD 여야 합니다 — ${metas[0].asOf}`);
  for (const [label, ids] of [
    ["lane", lanes.map((x) => x.id)],
    ["node", nodes.map((x) => x.id)],
    ["gap", gaps.map((x) => x.id)],
    ["doc", docs.map((x) => x.id)],
  ] as const)
    for (const id of duplicates([...ids])) errors.push(`${label} id 가 겹칩니다 — ${id}`);
  const laneIds = new Set(lanes.map((x) => x.id));
  const nodeIds = new Set(nodes.map((x) => x.id));
  const gapIds = new Set(gaps.map((x) => x.id));
  const cells = new Set<string>();
  for (const node of nodes) {
    if (!laneIds.has(node.lane)) errors.push(`node ${node.id}: 없는 lane '${node.lane}'`);
    if (node.gap && !gapIds.has(node.gap)) errors.push(`node ${node.id}: 없는 gap '${node.gap}'`);
    const cell = `${node.lane}/${node.row}`;
    if (cells.has(cell)) errors.push(`node ${node.id}: lane '${node.lane}' 의 row ${node.row} 에 이미 노드가 있습니다`);
    cells.add(cell);
  }
  for (const edge of edges) {
    if (!nodeIds.has(edge.from)) errors.push(`edge: 없는 from '${edge.from}'`);
    if (!nodeIds.has(edge.to)) errors.push(`edge: 없는 to '${edge.to}'`);
  }
  if (errors.length) return { blueprint: null, errors };
  return {
    errors,
    blueprint: {
      meta: metas[0],
      lanes,
      nodes,
      edges,
      flow: of<Step>("flow"),
      features: of<Feature>("feature"),
      gaps,
      docs,
    },
  };
}

// 근거 코드 경로 검사용: 어느 항목이 어떤 경로를 주장하는지.
export function claimedPaths(bp: Blueprint): { owner: string; path: string }[] {
  return [
    ...bp.nodes.flatMap((n) => (n.paths || []).map((path) => ({ owner: `node ${n.id}`, path }))),
    ...bp.gaps.flatMap((g) => (g.paths || []).map((path) => ({ owner: `gap ${g.id}`, path }))),
  ];
}
