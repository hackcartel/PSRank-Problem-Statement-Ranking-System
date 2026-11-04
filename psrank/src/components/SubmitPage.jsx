import { useState } from "react";
import { analyzeWithApi } from "../lib/api";
import { supabase } from "../lib/supabaseClient";
import GithubIcon from "./GithubIcon";

function SubmitPage({ user, onSignIn, redirecting }) {
  const [problem, setProblem] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const wordCount = problem.trim().split(/\s+/).filter(Boolean).length;

  async function submitProblem(event) {
    event.preventDefault();

    if (wordCount < 15) {
      setSubmitError("Please enter at least 15 words.");
      setAnalysis(null);
      return;
    }

    if (!user) {
      setSubmitError("Please sign in before submitting a problem.");
      return;
    }

    const problemText = problem.trim();
    setSubmitError("");
    setAnalysis(null);
    setAnalyzing(true);

    try {
      const result = await analyzeWithApi(problemText);

      const { error: saveError } = await supabase
        .from("problem_statements")
        .insert({
          user_id: user.id,
          text: problemText,
          score: result.score,
          category: result.category,
          breakdown: result.breakdown,
          similar: result.similar ?? [],
          reason: result.reason ?? "",
        });

      if (saveError) {
        throw saveError;
      }

      setAnalysis({
        ...result,
        totalScore: result.score,
      });
    } catch (error) {
      setSubmitError(
        error instanceof Error
          ? error.message
          : error?.message || "Analysis or save failed.",
      );
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <main className="page-content">
      <section className="page-heading">
        <p className="eyebrow">SHARE AN IDEA</p>
        <h1>Submit a problem</h1>
        <p>Describe a real challenge and see how it scores.</p>
      </section>

      {!user ? (
        <section className="submit-card signed-out-submit">
          <h2>Please sign in with GitHub to submit a problem</h2>
          <button
            className="github-button submit-login-button"
            type="button"
            onClick={onSignIn}
            disabled={redirecting}
          >
            <GithubIcon className="github-icon" />
            {redirecting ? "Connecting to GitHub…" : "Continue with GitHub"}
          </button>
        </section>
      ) : (
        <section className="submit-card">
          <form onSubmit={submitProblem} noValidate>
            <label htmlFor="problem-description">Problem statement</label>
            <textarea
              id="problem-description"
              value={problem}
              onChange={(event) => {
                setProblem(event.target.value);
                setSubmitError("");
                setAnalysis(null);
              }}
              placeholder="Describe who is affected, what challenge they face, and why it matters…"
              rows={9}
            />

            <div className="textarea-meta" aria-live="polite">
              <span>{problem.length} characters</span>
              <span>
                {wordCount} words{" "}
                <span className="counter-hint">(minimum 15)</span>
              </span>
            </div>

            {submitError && (
              <p className="form-error" role="alert">
                {submitError}
              </p>
            )}

            <button
              className="primary-button analyze-button"
              type="submit"
              disabled={analyzing}
            >
              {analyzing ? "Analyzing…" : "Analyze problem"}
            </button>
          </form>

          {analysis && (
            <section className="analysis-card" aria-live="polite">
              <div className="analysis-heading">
                <div>
                  <p className="eyebrow">ANALYSIS RESULT</p>
                  <h2>Your problem score</h2>
                </div>
                <strong className="total-score">
                  {analysis.totalScore}
                  <span>/100</span>
                </strong>
              </div>

              <span className="category-chip">{analysis.category}</span>

              <div className="breakdown-list">
                {Object.entries(analysis.breakdown ?? {}).map(([label, score]) => (
                  <div className="breakdown-row" key={label}>
                    <span>{label}</span>
                    <div
                      className="score-track"
                      role="progressbar"
                      aria-label={`${label} score`}
                      aria-valuemin="0"
                      aria-valuemax="10"
                      aria-valuenow={score}
                    >
                      <span style={{ width: `${score * 10}%` }} />
                    </div>
                    <strong>{score}/10</strong>
                  </div>
                ))}
              </div>

              <p className="analysis-reason">{analysis.reason}</p>
            </section>
          )}
        </section>
      )}
    </main>
  );
}

export default SubmitPage;