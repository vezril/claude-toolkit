// Shared parsing for the writing-for-agents asserts.
// strict:  the reply is the files the request asked for, each a "### <path>" heading
//          followed by one fenced block (w-03: a single "description:" line)
// lenient: whatever files can be recovered (headed blocks, else bare fenced blocks,
//          else the whole reply as the main file), so a format slip costs only format.
const fs = require('fs');
const path = require('path');

const spec = (context) =>
  JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'expected', context.vars.case + '.json'), 'utf8'));
const criteria = (s) => s.criteria;
const result = (problems, ok) =>
  problems.length ? { pass: false, score: 0, reason: problems.join('; ') } : { pass: true, score: 1, reason: ok };
const has = (re, s) => new RegExp(re, 'i').test(s);
const count = (re, s) => (String(s).match(new RegExp(re, 'gi')) || []).length;

// "### path" then a fence of 3+ backticks or tildes, closed by the same fence.
function headedFiles(out) {
  const re = /^#{2,4}\s+`?([^\s`]+)`?\s*\n+(`{3,}|~{3,})[^\n]*\n([\s\S]*?)\n\2\s*$/gm;
  return [...String(out).matchAll(re)].map((m) => ({ path: m[1], text: m[3] }));
}
function bareBlocks(out) {
  return [...String(out).matchAll(/^(`{3,}|~{3,})[^\n]*\n([\s\S]*?)\n\1\s*$/gm)].map((m, i) => ({ path: i ? `extra-${i}` : 'main', text: m[2] }));
}
function files(out) {
  const h = headedFiles(out);
  if (h.length) return h;
  const b = bareBlocks(out);
  if (b.length) return b;
  return [{ path: 'main', text: String(out) }];
}
// The main file: named like the original, else the one with frontmatter, else the first.
function mainFile(fs_, s) {
  return fs_.find((f) => s.main && path.basename(f.path).toLowerCase() === s.main.toLowerCase())
    || fs_.find((f) => /^---\n[\s\S]*?\bname:/.test(f.text)) || fs_[0];
}
function description(text) {
  const fm = String(text).match(/^---\n([\s\S]*?)\n---/);
  const src = fm ? fm[1] : String(text);
  const m = src.match(/^description:\s*(?:>-?\s*\n)?([\s\S]*?)(?=\n[a-z_-]+:|$)/m);
  return m ? m[1].replace(/^["']|["']$/g, '').replace(/\s+/g, ' ').trim() : null;
}
// Numbered steps: "1. text" plus its continuation lines, stopping at the next item,
// a blank line followed by a non-indented line, or a heading.
function steps(text) {
  const lines = String(text).split('\n');
  const out = [];
  let cur = null;
  for (const l of lines) {
    if (/^\s{0,3}\d+[.)]\s+/.test(l)) { cur = [l]; out.push(cur); continue; }
    if (!cur) continue;
    if (/^#/.test(l)) { cur = null; continue; }
    if (/^\s*$/.test(l)) { cur.push(''); continue; }
    if (/^\s+\S/.test(l) || cur[cur.length - 1] !== '') cur.push(l); else cur = null;
  }
  return out.map((c) => c.join('\n').trim());
}
const DONE = '\\b(done when|complete when|completed when|finished when|finish(ed)? only when|only when|stop when|is done once|done once|before (reporting|declaring|calling it) done|until (every|each|all)|until (every|each|all|you have|you can|the user (has )?confirm)|when (every|each|all) )|\\bdone\\b\\s*[:—-]|completion criteri';
const words = (s) => String(s).trim().split(/\s+/).filter(Boolean);

const body = (t) => String(t).replace(/^---\n[\s\S]*?\n---\n?/, '');

module.exports = { body, spec, criteria, result, has, count, files, headedFiles, mainFile, description, steps, DONE, words };
