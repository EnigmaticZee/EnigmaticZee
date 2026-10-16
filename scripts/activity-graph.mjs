#!/usr/bin/env node
// Renders assets/activity-graph.svg: the last 35 days of contributions as an
// "exposure strip" in the studio palette. Runs daily from GitHub Actions.
// No dependencies — Node 20+ (global fetch).

import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const USER = process.env.GRAPH_USER || 'EnigmaticZee';
const TOKEN = process.env.GITHUB_TOKEN;
const DAYS = 35;
const OUT = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'assets', 'activity-graph.svg');

const C = {
  bg: '#0e0c14', bar: '#16131f', border: '#2c2740', grid: '#1d1929',
  text: '#ece9f5', muted: '#8a84a3', dim: '#4d4766',
  violet: '#a78bfa', amber: '#f2c14e', mint: '#6ee7b7',
};
const MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Courier New', monospace";

if (!TOKEN) { console.error('GITHUB_TOKEN is required'); process.exit(1); }

const to = new Date();
const from = new Date(to.getTime() - (DAYS - 1) * 86400000);
const query = `query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){ contributionsCollection(from:$from,to:$to){
    contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }`;

const res = await fetch('https://api.github.com/graphql', {
  method: 'POST',
  headers: { Authorization: `bearer ${TOKEN}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ query, variables: { login: USER, from: from.toISOString(), to: to.toISOString() } }),
});
const json = await res.json();
if (!res.ok || json.errors) { console.error(JSON.stringify(json, null, 2)); process.exit(1); }

const days = json.data.user.contributionsCollection.contributionCalendar.weeks
  .flatMap((w) => w.contributionDays).slice(-DAYS);

// ---- layout
const W = 842, H = 230, PAD_X = 24, TOP = 70, BASE = 186;
const span = W - PAD_X * 2;
const slot = span / days.length;
const barW = Math.max(6, slot - 6);
const max = Math.max(1, ...days.map((d) => d.contributionCount));
const total = days.reduce((s, d) => s + d.contributionCount, 0);
const active = days.filter((d) => d.contributionCount > 0).length;
let streak = 0;
for (let i = days.length - 1; i >= 0; i--) {
  if (days[i].contributionCount > 0) streak++;
  else if (i === days.length - 1) continue; // today may still be empty
  else break;
}
const peak = days.reduce((a, b) => (b.contributionCount > a.contributionCount ? b : a));

const fmt = (iso) => new Date(iso + 'T00:00:00Z')
  .toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });

const bars = days.map((d, i) => {
  const x = PAD_X + i * slot + (slot - barW) / 2;
  const h = d.contributionCount === 0 ? 2 : Math.max(6, (d.contributionCount / max) * (BASE - TOP));
  const y = BASE - h;
  const fill = d === peak && d.contributionCount > 0 ? C.amber : d.contributionCount === 0 ? C.border : C.violet;
  const delay = (i * 0.03).toFixed(2);
  return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="${fill}" opacity="0">
      <title>${fmt(d.date)}: ${d.contributionCount} contribution${d.contributionCount === 1 ? '' : 's'}</title>
      <animate attributeName="opacity" from="0" to="1" begin="${delay}s" dur="0.4s" fill="freeze"/>
    </rect>`;
}).join('\n    ');

const gridLines = [0.25, 0.5, 0.75, 1].map((f) => {
  const y = BASE - f * (BASE - TOP);
  return `<line x1="${PAD_X}" y1="${y}" x2="${W - PAD_X}" y2="${y}" stroke="${C.grid}" stroke-dasharray="2 4"/>`;
}).join('\n  ');

const stat = (x, label, value, color) =>
  `<text x="${x}" y="50" font-family="${MONO}" font-size="12"><tspan fill="${C.muted}">${label} </tspan><tspan fill="${color}" font-weight="bold">${value}</tspan></text>`;

const svg = `<svg viewBox="0 0 ${W} ${H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${total} contributions in the last ${DAYS} days">
  <rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="12" fill="${C.bg}" stroke="${C.border}"/>
  <text x="${PAD_X}" y="26" fill="${C.text}" font-family="${MONO}" font-size="13" font-weight="bold">exposure log</text>
  <text x="${PAD_X + 112}" y="26" fill="${C.dim}" font-family="${MONO}" font-size="12">// last ${DAYS} days of shipping</text>
  ${stat(PAD_X, 'total', total, C.violet)}
  ${stat(PAD_X + 160, 'active days', `${active}/${DAYS}`, C.mint)}
  ${stat(PAD_X + 330, 'streak', `${streak}d`, C.amber)}
  ${stat(PAD_X + 450, 'peak', `${peak.contributionCount} · ${fmt(peak.date)}`, C.text)}
  ${gridLines}
  <line x1="${PAD_X}" y1="${BASE + 0.5}" x2="${W - PAD_X}" y2="${BASE + 0.5}" stroke="${C.border}"/>
    ${bars}
  <text x="${PAD_X}" y="${BASE + 24}" fill="${C.dim}" font-family="${MONO}" font-size="11">${fmt(days[0].date)}</text>
  <text x="${W - PAD_X}" y="${BASE + 24}" fill="${C.dim}" font-family="${MONO}" font-size="11" text-anchor="end">today</text>
</svg>
`;

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, svg);
console.log(`wrote ${OUT}: ${total} contributions, ${active} active days`);
