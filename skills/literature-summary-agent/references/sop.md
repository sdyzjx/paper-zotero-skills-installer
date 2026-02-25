# Literature Reading SOP

Use this SOP exactly when summarizing a paper.

## 1) Logic Layer: Derive the Innovation from the Problem

Extract one chain from Introduction and related sections:

Problem -> Existing methods -> Limitation -> Root cause -> New idea -> Innovation point

Answer these three questions explicitly:
- Problem: What exact problem does the paper solve?
- Gap: Why are existing methods not enough?
- Reasoning: What thinking path leads to the proposed innovation?

Rule:
- Focus on "why this idea" rather than only "what was done".

## 2) Structure Layer: Decompose Each Innovation

For each innovation point, write three parts:
- Principle: theoretical intuition, assumptions, objective, or modeling rationale
- Implementation: architecture/algorithm/training path/inference procedure
- Effect: what this innovation improves (performance, efficiency, robustness, generalization)

Goal:
- Make the method reproducible as engineering logic, not just concept-level description.

## 3) Evidence Layer: Evaluate Causal Support

Judge whether experiments truly support claims:
- Does the full method outperform strong baselines fairly?
- Do ablations isolate each innovation point?
- Are experiments designed to validate core hypotheses?

Core question:
- "Do these experiments actually support the paper's causal claims?"

## 4) Mandatory Refinement Pass (Second Pass)

After drafting the first version, run a mandatory second pass:
- Re-check all three layers for paper-specific reasoning (not generic prose).
- Ensure evidence section contains reproducible details:
  - experiment setup (dataset/hardware/protocol),
  - numeric outcomes (metrics + values),
  - baseline and ablation statements.
- Remove placeholders and weak template language (`待补充`, `TBD`, `TODO`, empty bullets).
- Recompile LaTeX after refinement and only then mark the summary complete.

## One-sentence framing
This SOP is a three-layer analysis:
- Logic layer: how the problem is derived into innovation
- Structure layer: how innovation is implemented
- Evidence layer: how innovation is validated
