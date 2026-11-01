# PSRank analyzer

Install dependencies from this folder with `python -m pip install -r requirements.txt`.

```python
from analyzer.analyze import analyze

result = analyze("Farmers need an app to monitor crop health.")
```

`analyze(text)` returns the score, five-part breakdown, category, similar statements,
and reason in the backend integration format. To compare with saved statements,
pass them as `existing_problems=[{"id": 12, "text": "..."}]`. Similarity uses
TF-IDF/cosine similarity and reports matches above `0.6`. LLM scoring is a
placeholder; the analyzer currently uses the weighted rule-based scorer.

Run tests from the repository root with `python -m unittest discover -s analyzer -v`.