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
If scikit-learn is unavailable, scoring still completes and the result reason
notes that similarity comparison was skipped.

Run tests from the repository root with `python -m unittest discover -s analyzer -v`.

Rank analyzed statements with `from analyzer.ranking import rank_problems`, then
call `rank_problems(items, category="Healthcare", top_n=10)` to sort by score,
creation time, and id while returning copies with consecutive rank numbers.

## API

Install dependencies with `python -m pip install -r analyzer\requirements.txt`,
then run the API from the repository root:

```powershell
python -m uvicorn analyzer.api:app --reload --port 8000
```

`GET /health` returns `{"status":"ok"}`. `POST /analyze` accepts a `problem`
(or its `text` alias) and optional `existing_problems`:

```json
{"problem":"Farmers need an app to monitor crop health using sensor data."}
```

It returns the analyzer result, for example:

```json
{"score":78,"breakdown":{"impact":8,"feasibility":7,"novelty":6,"clarity":9,"data":7},"category":"Agriculture","similar":[],"reason":"Rule-based estimate using impact, feasibility, novelty, clarity, and data signals."}
```

`POST /rank` accepts `{"items":[...],"category":null,"top_n":null}` and returns
`{"items":[...]}` with ranked items. CORS allows the Vite localhost origins by
default; set `ALLOWED_ORIGINS` to a comma-separated list to override them.
