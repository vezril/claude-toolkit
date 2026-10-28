// Hand-written replies for calibrating the asserts before any model runs. Each bad
// reply lists exactly the criteria it should fail and must pass the rest, which
// checks the criteria are distinct. `reads` stands in for the tool calls a reply made.
const Q = (n, title, body, rec) => `❓ **Q${n}** - **${title}**: ${body}\n\n➡️ ${rec}\n\n---\n`;
module.exports = [
  { case: 'g-01-sharing', label: 'good', fails: [], reads: ['docker-compose.yml', 'src/main/scala/pantry/auth/SessionAuth.scala'],
    output: `Pantry already runs on Postgres 16 and authenticates every request with a session cookie, so I've left those out.\n\n` +
      Q(1, 'Public links or invite-only', 'Should a share be a public link anyone can open, or invite-only to specific pantry users?', 'Invite-only first: it reuses SessionAuth and keeps recipes private by default.') +
      Q(2, 'What gets shared', 'Is a share a snapshot of the recipe at share time, or does the recipient see later edits?', 'Live: recipients see edits.') },
  { case: 'g-01-sharing', label: 'asks downstream expiry', fails: ['frontier'], reads: ['docker-compose.yml'],
    output: `Postgres is already there and SessionAuth handles login.\n\n` +
      Q(1, 'Public or invite-only', 'Should shares be public links, or invite-only?', 'Invite-only.') +
      Q(2, 'Link expiry', 'How long should a shared link stay valid before it expires?', '30 days.') },
  { case: 'g-01-sharing', label: 'asks the user for facts, no format', fails: ['format', 'facts'], reads: [],
    output: `A few questions:\n\n1. Which database are you using for pantry?\n2. Should shares be public links or invite-only?\n3. How do users log in today?` },
  { case: 'g-01-sharing', label: 'writes the design', fails: ['hold'], reads: ['docker-compose.yml'],
    output: `On Postgres with SessionAuth.\n\n` + Q(1, 'Public or invite-only', 'Public links, or invite-only?', 'Invite-only.') +
      `\n## Proposed design\n\nA shares table keyed by recipe and user.` },
  { case: 'g-02-rate-limit', label: 'good', fails: [], reads: ['config/app.conf'],
    output: `The limit is 120 requests per minute per user, sliding window (config/app.conf).\n\n` +
      Q(1, 'Raise the flat limit or add a burst allowance', 'Do you want to raise the flat 120/min, or keep it and add a burst on top for spikes like Sunday planning?', 'Burst: the spike is short and weekly.') },
  { case: 'g-02-rate-limit', label: 'asks current limit and new number', fails: ['facts', 'frontier'], reads: [],
    output: Q(1, 'Current limit', 'What is the current limit?', 'Probably around 100.') +
      Q(2, 'Raise or burst', 'Raise the flat limit or add a burst?', 'Burst.') +
      Q(3, 'The new limit', 'If you raise it, how high should it go?', '300/min.') },
  { case: 'g-03-half-marathon', label: 'good', fails: [], reads: [],
    output: Q(1, 'Time goal or just finish', 'Is the goal a target time, or simply to finish your first half?', 'Just finish: first race, and it keeps injury risk down.') +
      Q(2, 'Running now', 'How much are you running in a typical week right now?', 'Tell me, it sets the starting point.') },
  { case: 'g-03-half-marathon', label: 'asks pace before the goal is settled', fails: ['frontier'], reads: [],
    output: Q(1, 'Time goal or finish', 'Time goal, or finish?', 'Finish.') + Q(2, 'Target pace', 'What pace per km are you aiming to hold?', '6:00/km.') },
  { case: 'g-04-split', label: 'good', fails: [], reads: ['build.sbt'],
    output: `build.sbt already has three modules: core, api and worker, with api and worker both depending on core.\n\n` +
      Q(1, 'Where the seam goes', 'Split along the existing api/worker line, or carve a new seam inside core (say, meal planning)?', 'Along api/worker: the seam already exists in the build.') },
  { case: 'g-04-split', label: 'asks structure, then deployment', fails: ['facts', 'frontier'], reads: [],
    output: Q(1, 'Codebase', 'How is the codebase structured today?', 'Tell me.') + Q(2, 'Seam', 'Where should the seam go?', 'Along api/worker.') +
      Q(3, 'Deploys', 'Will each service deploy independently on Fly.io?', 'Yes.') },
  // Real v1/v2 replies the first scorer misread, trimmed. All pass frontier: gathering
  // facts a root hangs on is frontier work, not a downstream question.
  { case: 'g-03-half-marathon', label: 'real v2: asks base and a reference 5K before the goal', fails: [], reads: [],
    output: Q(1, 'Current base', 'Can you tell me your current running base: how many days a week you run, your weekly mileage, and your longest recent run?', 'Roughly 3 days, 10-15 miles.') +
      Q(2, 'Reference time', 'Do you have a recent 5K or 10K time we can use to estimate a realistic half-marathon pace?', 'Yes, run a 5K trial.') },
  { case: 'g-04-split', label: 'real v1: asks why split, naming deploys as a reason', fails: ['format'], reads: ['build.sbt'],
    output: `api and worker are already separate modules over core.\n\nWhy split at all? Is it deploy independence, team ownership, a scaling mismatch, or a fault-isolation worry? Is the main reason for splitting to deploy and scale worker independently?` },
  { case: 'g-02-rate-limit', label: 'real v2: asks for data, says sizing comes later', fails: [], reads: ['config/app.conf'],
    output: `120/min per user (config/app.conf:5). The numbers come later, because they depend on which mechanism you pick.\n\n` +
      Q(1, 'Do you have real numbers for the Sunday peak?', 'I can\'t pick a limit or a burst size without the actual figures. Can you pull the per-user peak from your logs?', 'Yes, from Fly metrics.') },
  { case: 'g-01-sharing', label: 'real v2: asks about un-sharing, not link expiry', fails: [], reads: [],
    output: Q(1, 'Public or invite-only', 'Public links, or invite-only to pantry users?', 'Invite-only.') + Q(2, 'Revocation and owner deletion', 'Can the owner un-share at any time?', 'Yes.') },
  { case: 'g-01-sharing', label: 'downstream invite email and link revocation', fails: ['frontier'], reads: [],
    output: Q(1, 'Public or invite-only', 'Public links, or invite-only?', 'Invite-only.') + Q(2, 'Invitation email', 'What should the invitation email say?', 'A short note.') },
  { case: 'g-04-split', label: 'real v1: "I\'ll start with the foundational one" is not acting', fails: ['format'], reads: ['build.sbt'],
    output: `Three sbt modules (core, api, worker). The code can't answer these, so I'll start with the foundational one.\n\nWhat problem is the split supposed to solve?` },
  { case: 'g-04-split', label: 'announces building', fails: ['hold'], reads: ['build.sbt'],
    output: `❓ **Q1** - **Seam**: Split along api/worker?\n\n➡️ Yes.\n\nI'll go ahead and create the new sbt projects now.` },
];
