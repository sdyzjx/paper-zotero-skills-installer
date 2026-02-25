# Output Contract

## Matrix CSV schema
Use this column order:

rank,title,year,source,doi_or_arxiv,citations,impact_score,topic_bucket,key_contribution,evidence_strength,zotero_item_key,summary_path

## Recommended folder layout

- 01_selection/top_candidates.csv
- 01_selection/top_final.csv
- 02_pdfs/arxiv/
- 02_pdfs/ieee/
- 03_summaries/<paper-slug>/main.tex
- 03_summaries/<paper-slug>/main.pdf
- 03_summaries/<paper-slug>/deep_reading.md
- 04_overview/TopN_Matrix.csv
- 04_overview/TopN_Comparative_Report.md
- 04_overview/<Full_Review>.tex
- 04_overview/<Full_Review>.pdf

## Minimum per-paper deep reading fields

- Problem definition and gap
- Method derivation chain
- Experiment setup (dataset/env/hardware/metrics)
- Quantitative results (tables/numbers)
- Evidence strength and limitations
