# Artifact schemas

One schema per structured artifact in `delivery/<ITEM-KEY>/`. Each schema declares:

- `artifact`: the file name it governs;
- `produced_by`: the step that writes it;
- `consumed_by`: the steps that read it;
- `counts`: named count expressions the node's sentinel must claim, so a node that
  believes it wrote 8 stories over a file holding 5 fails its edge;
- `consumers`: per consuming step, the fields that step requires — this is the
  input-contract half of an edge ("node A's output matches one of node B's inputs").

The schema language is a JSON Schema subset implemented by `scripts/delivery-flow/validate-artifact.py`
with the standard library only: `type`, `required`, `properties`, `items`, `enum`, `const`,
`pattern`, `minLength`, `minItems`, `additionalProperties`.

Count expressions: `epics[]` is the number of epics; `epics[].stories[]` is the total
number of stories across epics.

Artifacts are JSON. The Stage 4 course writes its breakdown example in YAML; JSON is the
same contract without adding a YAML parser dependency to every machine that runs a check.
