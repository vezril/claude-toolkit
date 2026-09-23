// Criterion 1 — contract (strict). The output IS the PR description:
// no preamble, no wrapping code fence, exactly the three sections the skill
// defines, in order, a one-sentence What, and a bulleted Changes list.
// No leniency here on purpose: this criterion owns every formatting penalty.

const { result } = require('./lib');

module.exports = (output) => {
  const problems = [];
  const text = String(output).replace(/\r\n/g, '\n').trim();

  if (!text.startsWith('## What')) {
    problems.push('does not start with "## What" (preamble or fence before the description)');
  }
  if (/^```/m.test(text)) problems.push('contains a code fence');

  const headings = (text.match(/^##\s+.+$/gm) || []).map((h) => h.replace(/^##\s+/, '').trim());
  const want = ['What', 'Why', 'Changes'];
  if (headings.join('|') !== want.join('|')) {
    problems.push('H2 sections are [' + headings.join(', ') + '], expected exactly [What, Why, Changes] in order');
  }

  const section = (name) => {
    const m = text.match(new RegExp('^##\\s+' + name + '\\s*$([\\s\\S]*?)(?=^##\\s|$(?![\\s\\S]))', 'm'));
    return m ? m[1].trim() : '';
  };

  const what = section('What');
  // Sentence ends: . ! ? followed by whitespace or end. Dots inside file names
  // (backoff.py, build.sbt) are not followed by whitespace, so they don't count.
  const sentences = what.split(/[.!?](?=\s|$)/).map((s) => s.trim()).filter((s) => s.length > 0);
  if (sentences.length !== 1) problems.push('## What has ' + sentences.length + ' sentences (skill says one)');

  const why = section('Why');
  if (!why) problems.push('## Why is empty');

  const changes = section('Changes');
  const lines = changes.split('\n').map((l) => l.trimEnd()).filter((l) => l.trim().length > 0);
  if (!lines.length) problems.push('## Changes is empty');
  const nonBullets = lines.filter((l) => !/^\s*[-*]\s+\S/.test(l));
  if (nonBullets.length) problems.push('## Changes has ' + nonBullets.length + ' non-bullet line(s), e.g. "' + nonBullets[0].slice(0, 60) + '"');

  return result(problems, 'contract ok: 3 sections in order, 1-sentence What, ' + lines.length + ' bullets');
};
