import { useEffect, useMemo, useState } from "react";
import { rankWithApi } from "../lib/api";
import { supabase } from "../lib/supabaseClient";

function getProblemParts(value) {
  const text = (value || "").replace(/\s+/g, " ").trim();

  if (!text) {
    return { title: "Problem statement", description: "" };
  }

  const sentenceEnd = text.search(/[.!?](?:\s|$)/);

  if (sentenceEnd > 0 && sentenceEnd < 90) {
    return {
      title: text.slice(0, sentenceEnd + 1),
      description: text.slice(sentenceEnd + 1).trim(),
    };
  }

  const cutoff = Math.min(82, text.length);

  return {
    title: cutoff < text.length ? `${text.slice(0, cutoff).trimEnd()}…` : text,
    description: cutoff < text.length ? text.slice(cutoff).trim() : "",
  };
}

function RankingsPage() {
  const [category, setCategory] = useState("All");
  const [rows, setRows] = useState([]);
  const [problems, setProblems] = useState([]);
  const [rowsLoading, setRowsLoading] = useState(true);
  const [rankingLoading, setRankingLoading] = useState(true);
  const [dataError, setDataError] = useState("");
  const [rankError, setRankError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadProblems() {
      setRowsLoading(true);
      setDataError("");

      const { data, error } = await supabase
        .from("problem_statements")
        .select("*");

      if (!active) return;

      if (error) {
        setDataError(error.message);
        setRows([]);
      } else {
        setRows(data ?? []);
      }

      setRowsLoading(false);
    }

    loadProblems().catch((error) => {
      if (!active) return;
      setDataError(error instanceof Error ? error.message : "Could not load problem statements.");
      setRowsLoading(false);
    });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (rowsLoading || dataError) return;

    let active = true;
    setRankingLoading(true);
    setRankError("");

    rankWithApi(rows, category)
      .then((rankedItems) => {
        if (active) setProblems(rankedItems);
      })
      .catch((error) => {
        if (!active) return;
        setRankError(
          error instanceof Error ? error.message : "Could not rank problem statements.",
        );
      })
      .finally(() => {
        if (active) setRankingLoading(false);
      });

    return () => {
      active = false;
    };
  }, [rows, category, rowsLoading, dataError]);

  const categories = useMemo(
    () =>
      [...new Set(rows.map((item) => item.category).filter(Boolean))].sort((a, b) =>
        a.localeCompare(b),
      ),
    [rows],
  );

  const error = dataError || rankError;

  return (
    <main className="page-content">
      <section className="page-heading">
        <p className="eyebrow">THE COMMUNITY’S PICKS</p>
        <h1>Problem rankings</h1>
        <p>Explore the ideas the community believes are worth solving.</p>
      </section>

      <section className="ranking-section ranking-page" aria-label="Problem rankings">
        <div className="section-heading">
          <div>
            <p className="eyebrow">LEADERBOARD</p>
            <h2>Top problem statements</h2>
          </div>

          <label className="filter-control">
            <span>Category</span>
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              <option value="All">All</option>
              {categories.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error ? (
          <div className="empty-state" role="alert">
            <h3>Could not load rankings</h3>
            <p>{error}</p>
          </div>
        ) : rowsLoading || rankingLoading ? (
          <div className="empty-state" aria-live="polite">
            <h3>Loading rankings…</h3>
          </div>
        ) : problems.length > 0 ? (
          <ol className="ranking-list">
            {problems.map((item, index) => {
              const text = item.text || item.description || "";
              const { title, description } = getProblemParts(text);
              const rank = item.rank ?? index + 1;
              const hasSimilar = Array.isArray(item.similar)
                ? item.similar.length > 0
                : Boolean(item.similar);

              return (
                <li className="ranking-row" key={item.id}>
                  <span
                    className={`rank-number ${rank <= 3 ? `rank-${rank}` : ""}`}
                    aria-label={`Rank ${rank}`}
                  >
                    {rank}
                  </span>

                  <div className="ranking-problem">
                    <h3>{title}</h3>
                    {description && <p>{description}</p>}
                  </div>

                  <span className="category-chip">{item.category}</span>

                  {hasSimilar && <span className="similar-badge">Similar</span>}

                  <div
                    className="score-display"
                    aria-label={`Score ${item.score} out of 100`}
                  >
                    <div
                      className="score-track"
                      role="progressbar"
                      aria-label="Problem score"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      aria-valuenow={item.score}
                    >
                      <span style={{ width: `${item.score}%` }} />
                    </div>
                    <strong>{item.score}</strong>
                  </div>
                </li>
              );
            })}
          </ol>
        ) : (
          <div className="empty-state">
            <div className="empty-icon" aria-hidden="true">✳</div>
            <h3>No problem statements yet</h3>
            <p>Be the first to share an idea with the community.</p>
            <a className="primary-button" href="#submit">
              Submit a problem <span aria-hidden="true">→</span>
            </a>
          </div>
        )}
      </section>
    </main>
  );
}

export default RankingsPage;