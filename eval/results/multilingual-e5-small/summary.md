# intfloat/multilingual-e5-small evaluation

Reused 131 saved vectors; 16 answerable and 4 unanswerable questions.
Relevance labels validated: 0/16. Status: unavailable: manual relevance labels missing.

| Question language | Answerable questions | Hit@1 | Hit@5 | Hit@10 | MRR@10 |
| --- | --- | --- | --- | --- | --- |
| Overall | 16 | N/A | N/A | N/A | N/A |
| English | 6 | N/A | N/A | N/A | N/A |
| Roman Urdu | 5 | N/A | N/A | N/A | N/A |
| Urdu | 5 | N/A | N/A | N/A | N/A |

Warmed CPU query encoding plus NumPy search: p50 44.53 ms; p95 69.41 ms (60 samples). Model loading excluded.

Unanswerable retrieval is saved separately and excluded from relevance metrics.

For missing labels, review `manual_labeling_needed.jsonl` against the corpus. Source-reference candidates are not accepted labels. Review other chunks, including the other language, for equivalent evidence. For Q06 review both password and PIN passages.
Copy `relevance_labels_template.json` to `eval/relevance_labels.json`, enter relevant chunk IDs, and set `reviewed` to true only after manual review. Re-run the same evaluation command. Do not label by retrieval rank.

Hit@k and MRR@10 count the first hit among any relevant chunk; they do not measure complete multi-passage evidence coverage.
