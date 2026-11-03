import { useMemo, useState } from "react";
import { CATEGORIES, MOCK_PROBLEMS } from "../mockData";

function RankingsPage() {
  const [category, setCategory] = useState("All");
  const problems = useMemo(
    () => MOCK_PROBLEMS
      .filter((item) => category === "All" || item.category === category)
      .slice()
      .sort((a, b) => b.score - a.score || new Date(a.created_at) - new Date(b.created_at)),
    [category],
  );

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
              <option>All</option>
              {CATEGORIES.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
        </div>
        {problems.length ? (
          <ol className="ranking-list">
            {problems.map((item, index) => (
              <li className="ranking-row" key={item.id}>
                <span className={`rank-number ${index < 3 ? `rank-${index + 1}` : ""}`} aria-label={`Rank ${index + 1}`}>
                  {index + 1}
                </span>
                <div className="ranking-problem">
                  <h3>{item.title || item.description.split("\n")[0]}</h3>
                  <p>{item.description}</p>
                </div>
                <span className="category-chip">{item.category}</span>
                {item.similar && <span className="similar-badge">Similar</span>}
                <div className="score-display" aria-label={`Score ${item.score} out of 100`}>
                  <div
                    className="score-track"
                    role="progressbar"
                    aria-label={`${item.title} score`}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={item.score}
                  >
                    <span style={{ width: `${item.score}%` }} />
                  </div>
                  <strong>{item.score}</strong>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <div className="empty-state">
            <div className="empty-icon" aria-hidden="true">✳</div>
            <h3>No problems in this category yet</h3>
            <p>Be the first to share an idea for this category.</p>
            <a className="primary-button" href="#submit">Submit a problem <span aria-hidden="true">→</span></a>
          </div>
        )}
      </section>
    </main>
  );
}

export default RankingsPage;
