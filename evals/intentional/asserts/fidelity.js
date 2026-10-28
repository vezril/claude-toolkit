// Criterion 3, method fidelity: did the ritual do its job for this case? One check per
// case, keyed by vars.case. Reads the reply leniently and the written lines exactly.
// Formatting (questions, length, dashes) is friction's business and file damage is
// safety's, so neither is re-checked here.
const L = require('./lib');

const has = (s, re) => re.test(s || '');
function need(fails, cond, msg) { if (!cond) fails.push(msg); }
// Asked him something: a question mark, or an imperative request ("pick one for each").
const asks = (r) => L.questions(r) >= 1 || /\b(pick|choose|tell me|let me know|confirm|which)\b/i.test(L.prose(r));

function todayAdded(o) { const c = L.change(o, L.TODAY); return c ? L.added(c) : ''; }
function todayAfter(o) { const c = L.change(o, L.TODAY); return c ? c.after : ''; }

function firstStep(fails, r) {
  need(fails, has(r, L.TIME), 'no time in the first step');
  need(fails, has(r, L.PLACE), 'no place in the first step');
}

const checks = {
  // ── intentional-daily ──────────────────────────────────────────────────
  'd1-morning-blank': (o, r, f) => {
    need(f, has(r, /chapter 4|cloud cert|cert/i) && has(r, /tax/i) && has(r, /\brun/i), "didn't show the week's three");
    need(f, has(r, /three/i) && asks(r), "didn't ask for the day's three");
  },
  'd2-morning-full': (o, r, f) => {
    const a = todayAdded(o), after = todayAfter(o);
    need(f, !!a, "didn't write today's note");
    if (!a) return;
    need(f, has(a, /^## Intentions/m) || has(after, /^## Intentions/m), 'no ## Intentions section');
    const items = (a.match(/^(> ?)?- \[ \] .+/gm) || []);
    need(f, items.length === 3, `${items.length} unchecked items written (want 3)`);
    for (const e of ['Google Professional Cloud Developer', 'Being Financially Stable', 'I want to learn Japanese']) {
      need(f, a.includes(`[[${e}]]`), `no [[${e}]] link`);
    }
    need(f, has(a, /\*\*Current intention:\*\*[^\n]*cert/i), 'current intention is not the cert');
    const step = (/\*\*First step for the dreaded one:\*\*([^\n]*)/.exec(a) || [])[1] || '';
    need(f, has(step, /1\s?pm|13:00|13h/i) && has(step, /kitchen/i) && has(step, /CRA|folder/i), `first-step line missing when/where/action: "${step.trim()}"`);
    need(f, has(after, /^## Distractions/m), 'no ## Distractions section');
  },
  'd3-morning-six': (o, r, f) => {
    need(f, has(r, /pick|choose|which three|narrow|favou?rite|top three|only three|cut|name (the |your )?three/i), "didn't ask him to pick three");
  },
  'd4-morning-dreaded': (o, r, f) => {
    need(f, has(r, /tax|receipt/i), "didn't address the dreaded tax item");
    firstStep(f, r);
    need(f, asks(r), "didn't ask him to confirm");
  },
  'e1-evening-trigger': (o, r, f) => {
    const after = todayAfter(o), a = todayAdded(o);
    need(f, has(after, /^- \[x\] Cloud cert chapter 5/im), 'cert not ticked');
    need(f, has(after, /^- \[x\] 20 min Japanese/im), 'Japanese not ticked');
    need(f, has(after, /^- \[ \] File September tax/im), 'tax item ticked or removed');
    need(f, has(a, /\*\*Close-out:\*\*\s*2\/3/), 'no "**Close-out:** 2/3" line');
    need(f, has(a, /tax[^\n]*aversion:\s*unpleasant/i), 'miss not tagged (aversion: unpleasant)');
    need(f, has(r, /aversion-breaker|aversion breaker|weekly review|goal review/i), "didn't flag the 4-day repeat (aversion-breaker / weekly review)");
  },
  'e2-evening-no-trigger': (o, r, f) => {
    const missing = L.TRIGGERS.filter((t) => !new RegExp(t.replace(' ', '[ -]'), 'i').test(r));
    need(f, missing.length === 0, `didn't offer triggers: ${missing.join(', ')}`);
    need(f, asks(r), "didn't ask");
  },
  'm1-midday-reset': (o, r, f) => {
    need(f, has(r, /cert/i) && has(r, /tax/i) && has(r, /japanese/i), "didn't show the three");
    need(f, asks(r), "didn't ask which is next");
    const after = todayAfter(o);
    const dist = (/^## Distractions\n([\s\S]*?)(?=^## |$(?![\s\S]))/m.exec(after) || [])[1] || '';
    need(f, has(dist, /reddit/i), 'Reddit urge not logged under ## Distractions');
  },

  // ── aversion-breaker ───────────────────────────────────────────────────
  'a1-bare': (o, r, f) => {
    const missing = L.TRIGGERS.filter((t) => !new RegExp(t.replace(' ', '[ -]'), 'i').test(r));
    need(f, missing.length === 0, `didn't offer triggers: ${missing.join(', ')}`);
    need(f, asks(r), "didn't ask which fits");
  },
  'a2-blog-unstructured': (o, r, f) => {
    need(f, has(r, /implementation intention|when.{0,40}where|habit stack|after (your |my )?(coffee|breakfast|dinner|lunch)|habit points/i), 'no unstructured strategy');
    firstStep(f, r);
  },
  'a3-boring': (o, r, f) => {
    need(f, has(r, /harder|gamif|personal best|sprint|race|timer|beat (your|the)|challenge/i), 'no boring strategy (harder / gamify)');
    firstStep(f, r);
  },
  'a4-blog-repeat': (o, r, f) => {
    need(f, has(r, /\b(third|fourth|3rd|4th) time|\b(3|4|three|four|several) times|(has|have|had) (come|came) up|came up|keeps coming|already tried|same task/i), "didn't notice the repeat");
    need(f, has(r, /weekly|goal review/i) && has(r, /edit|drop|backlog|pause|archive|rethink|shrink|smaller|rework/i), "didn't push to edit or drop it in the weekly review");
  },
  'a5-ikea-meaningless': (o, r, f) => {
    need(f, has(r, /matters because|why (it|this) matters|trace|intention stack|value|what('s| is) it for/i), "didn't trace it up the stack");
  },
  'a6-japanese-frustrating': (o, r, f) => {
    need(f, has(r, /learning goal|learn(ing)?[^.]{0,40}instead|performance|learn the (pattern|rule)|from "?get(ting)? it right/i), 'no performance-to-learning switch');
    firstStep(f, r);
  },

  // ── intentional-weekly ─────────────────────────────────────────────────
  'w1-quick': (o, r, f) => {
    const rows = r.split('\n').filter((l) => /^\s*\|/.test(l)).join('\n');
    need(f, has(rows, /effort/i) && has(rows, /aversion/i), 'no review table');
    const efforts = { cloud: /cloud|cert/i, japanese: /japanese/i, run: /\brun/i, drinking: /drink/i, blog: /blog/i, ikea: /ikea/i, finance: /financ/i };
    const missing = Object.keys(efforts).filter((k) => !efforts[k].test(rows));
    need(f, missing.length === 0, `table missing active efforts: ${missing.join(', ')}`);
    need(f, !/room/i.test(rows), 'table lists the completed room goal');
    // Two defensible readings: the last 7 notes incl. today's blank one (8/15),
    // or the 7 days before today (10/18).
    need(f, has(r, /\b(10\s*\/\s*18|10 of 18|8\s*\/\s*15|8 of 15)\b/), 'hit rate neither 8/15 nor 10/18');
    need(f, has(r, /three/i) && asks(r), "didn't ask for the week's three");
  },
  'w2-full-mom-goal': (o, r, f) => {
    need(f, r.split('\n').some((l) => /^\s*\|.*effort/i.test(l)), 'no review table');
    need(f, has(r, /drink/i) && has(r, /backlog|archive/i), "didn't propose moving the drinking goal to Backlog/Archive");
    need(f, has(r, /drop|let (it )?go|not (yours|your goal)|whose goal/i), "didn't name it as a drop / whose-goal");
    need(f, asks(r), "didn't ask for his OK");
  },
  'w3-plan-given': (o, r, f) => {
    const c = L.change(o, L.WEEK);
    const a = c ? L.added(c) : '';
    need(f, !!a, "didn't write the week note");
    if (!a) return;
    const items = a.match(/^(> ?)?- \[ \] .+/gm) || []; // a callout list is fine
    need(f, items.length === 3, `${items.length} unchecked items written (want 3)`);
    need(f, has(a, /chapter 5/i) && has(a, /\brun/i) && has(a, /accountant/i), "the week's three aren't the ones he gave");
    for (const e of ['Google Professional Cloud Developer', 'Run three times a week', 'Being Financially Stable']) {
      need(f, a.includes(`[[${e}]]`), `no [[${e}]] link`);
    }
  },
  'w4-new-goals': (o, r, f) => {
    need(f, has(r, /guitar/i) && has(r, /podcast/i), "didn't address the new goals");
    need(f, has(r, /no evidence|without evidence|stalled|barely started|haven't moved|not moving|no progress|too many|pick (your )?favou?rites|pause/i), "didn't push back on adding goals");
  },
};

module.exports = (output, { vars }) => {
  const o = L.parse(output);
  const check = checks[vars.case];
  if (!check) return { pass: false, score: 0, reason: `no fidelity check for case ${vars.case}` };
  const fails = [];
  check(o, o.reply || '', fails);
  return L.result(fails, 'ritual did its job');
};
