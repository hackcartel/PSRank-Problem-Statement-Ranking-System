import { useEffect, useState } from "react";
import { supabase } from "./lib/supabaseClient";
import { MOCK_PROBLEMS } from "./mockData";
import LoginPage from "./components/LoginPage";
import RankingsPage from "./components/RankingsPage";
import SubmitPage from "./components/SubmitPage";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [redirecting, setRedirecting] = useState(false);
  const [authError, setAuthError] = useState("");
  const [route, setRoute] = useState(() => window.location.hash.slice(1) || "dashboard");

  useEffect(() => {
    let active = true;
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!active) return;
      setUser(session?.user ?? null);
      setSessionLoading(false);
      setRedirecting(false);
      if (session?.user) setAuthError("");
    });

    supabase.auth.getSession().then(({ data, error }) => {
      if (!active) return;
      if (error) setAuthError(error.message);
      setUser(data.session?.user ?? null);
      setSessionLoading(false);
    }).catch((error) => {
      if (!active) return;
      setAuthError(error instanceof Error ? error.message : "Could not check your session.");
      setSessionLoading(false);
    });

    const onHashChange = () => setRoute(window.location.hash.slice(1) || "dashboard");
    window.addEventListener("hashchange", onHashChange);
    return () => {
      active = false;
      subscription.unsubscribe();
      window.removeEventListener("hashchange", onHashChange);
    };
  }, []);

  async function signInWithGithub() {
    setAuthError("");
    setRedirecting(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: { redirectTo: window.location.origin },
      });
      if (error) throw error;
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "GitHub sign-in could not be started.");
      setRedirecting(false);
    }
  }

  async function signOut() {
    setAuthError("");
    try {
      const { error } = await supabase.auth.signOut();
      if (error) setAuthError(error.message);
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Could not sign out.");
    }
  }

  const username = user?.user_metadata?.user_name || user?.email || "GitHub user";
  const avatarUrl = user?.user_metadata?.avatar_url;

  if (sessionLoading) {
    return (
      <main className="session-loading" aria-live="polite">
        <span className="loading-spinner" aria-hidden="true" />
        <p>Checking your session…</p>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#dashboard" aria-label="PSRank dashboard">
          PS<span>Rank</span>
        </a>
        {user && (
          <nav aria-label="Main navigation">
            <a className={route === "dashboard" ? "active" : ""} href="#dashboard">Dashboard</a>
            <a className={route === "rankings" ? "active" : ""} href="#rankings">Rankings</a>
            <a className={route === "submit" ? "active" : ""} href="#submit">Submit a problem</a>
          </nav>
        )}
        <div className="user-menu">
          {user ? (
            <>
              {avatarUrl && <img className="user-avatar" src={avatarUrl} alt={`${username}'s GitHub avatar`} />}
              <span className="user-name" title={username}>{username}</span>
              <button className="login-button" type="button" onClick={signOut}>Log out</button>
            </>
          ) : (
            <>
              <button className="login-button signup-nav-button" type="button" onClick={signInWithGithub} disabled={redirecting}>
                {redirecting ? "Redirecting…" : "Sign in with GitHub"}
              </button>
            </>
          )}
        </div>
      </header>

      {authError && <p className="global-error" role="alert">{authError}</p>}

      {!user ? (
        <LoginPage onSignIn={signInWithGithub} redirecting={redirecting} />
      ) : route === "rankings" ? (
        <RankingsPage />
      ) : route === "submit" ? (
        <SubmitPage user={user} onSignIn={signInWithGithub} redirecting={redirecting} />
      ) : (
        <main className="dashboard">
          <section className="welcome" id="dashboard">
            {user && <p className="signed-in-message">Signed in as {username}</p>}
            <p className="eyebrow">HACKCARTEL · PROBLEM STATEMENTS</p>
            <h1>Find the next problem<br />worth solving.</h1>
            <p className="intro">Explore the community’s problem statements and see what’s rising to the top.</p>
            <a className="primary-button" href="#rankings">Explore rankings <span aria-hidden="true">→</span></a>
          </section>
          <section className="ranking-section" id="rankings">
            <div className="section-heading">
              <div>
                <p className="eyebrow">THE COMMUNITY’S PICKS</p>
                <h2>Top problem statements</h2>
              </div>
              <a className="view-all" href="#rankings">View all →</a>
            </div>
            <div className="ranking-preview">
              {MOCK_PROBLEMS.slice()
                .sort((a, b) => b.score - a.score || new Date(a.created_at) - new Date(b.created_at))
                .slice(0, 3)
                .map((item, index) => (
                  <article className="preview-row" key={item.id}>
                    <span className={`rank-number rank-${index + 1}`}>{index + 1}</span>
                    <div>
                      <h3>{item.title}</h3>
                      <span className="category-chip">{item.category}</span>
                    </div>
                    <strong className="preview-score">{item.score}<span>/100</span></strong>
                  </article>
                ))}
            </div>
            <a className="primary-button" href="#rankings">View all rankings <span aria-hidden="true">→</span></a>
          </section>
        </main>
      )}

      <footer>Built by HackCartel</footer>
    </div>
  );
}

export default App;
