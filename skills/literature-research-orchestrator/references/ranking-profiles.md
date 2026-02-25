# Ranking Profiles (Scoring Method Templates)

Use one of these profiles when user asks for literature ranking.
Always confirm profile name + weight tuple + tie-break rule.

## Required scoring fields

Minimum fields in any profile:
- citations_impact
- venue_quality
- topical_relevance

Optional fields:
- recency
- methodological_novelty
- engineering_readiness
- evidence_strength

Total score must sum to 100.

## Profile A: 影响力优先 (Impact-First)

Best for: survey baseline building, high-confidence canonical papers.

Weights:
- citations_impact: 60
- venue_quality: 25
- topical_relevance: 15

Tie-break rule:
1. higher evidence_strength
2. newer publication date
3. broader benchmark coverage

## Profile B: 新颖性优先 (Novelty-First)

Best for: frontier scanning, emerging directions, early trend spotting.

Weights:
- methodological_novelty: 40
- topical_relevance: 25
- recency: 20
- venue_quality: 10
- citations_impact: 5

Tie-break rule:
1. stronger ablation/comparison design
2. open-source artifacts availability
3. lower overlap with already selected papers

## Profile C: 工程落地优先 (Deployment-First)

Best for: implementation roadmap, near-term adoption decisions.

Weights:
- engineering_readiness: 35
- evidence_strength: 25
- topical_relevance: 20
- venue_quality: 10
- citations_impact: 10

Tie-break rule:
1. hardware/real-world validation presence
2. reproducibility details (code, configs, seeds)
3. compute/resource feasibility

## Profile D: 平衡综合 (Balanced)

Best for: mixed portfolio selection where no single objective dominates.

Weights:
- citations_impact: 25
- venue_quality: 20
- topical_relevance: 25
- recency: 15
- evidence_strength: 15

Tie-break rule:
1. diversity across topic buckets
2. stronger quantitative gains
3. fewer unresolved limitations

## Custom profile template

When user provides custom scoring, normalize to this format:

```yaml
ranking_rule:
  profile_name: "custom"
  weights:
    citations_impact: <0-100>
    venue_quality: <0-100>
    topical_relevance: <0-100>
    recency: <0-100, optional>
    methodological_novelty: <0-100, optional>
    engineering_readiness: <0-100, optional>
    evidence_strength: <0-100, optional>
  tie_break:
    - "rule-1"
    - "rule-2"
    - "rule-3"
```

Validation:
- all weights are non-negative
- total weight = 100
- at least three scoring dimensions are active
