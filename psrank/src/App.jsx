import { supabase } from "./lib/supabaseClient";
import { useEffect, useState } from "react";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [user, setUser] = useState(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  async function handleLogout() {
    const { error } = await supabase.auth.signOut();

    if (error) {
      setLoginError(error.message);
    } else {
      setShowLogin(false);
      setLoginError("");
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setLoginError("");

    const formData = new FormData(event.currentTarget);
    const email = formData.get("email");
    const password = formData.get("password");

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setLoading(false);

    if (error) {
      setLoginError(error.message);
      return;
    }

    setShowLogin(false);
  }

  return (
    <main className="dashboard">
      <header className="topbar">
        <a
          className="brand"
          href="#dashboard"
          onClick={() => setShowLogin(false)}
        >
          PS<span>Rank</span>
        </a>

        <nav aria-label="Main navigation">
          <a className="active" href="#dashboard" onClick={() => setShowLogin(false)}>
            Dashboard
          </a>
          <a href="#rankings" onClick={() => setShowLogin(false)}>
            Rankings
          </a>
          <a href="#submit" onClick={() => setShowLogin(false)}>
            Submit a problem
          </a>
        </nav>

        {user ? (
          <div className="user-menu">
            <span className="user-email">{user.email}</span>
            <button className="login-button" type="button" onClick={handleLogout}>
              Log out
            </button>
          </div>
        ) : (
          <button
            className="login-button"
            type="button"
            onClick={() => setShowLogin(true)}
          >
            Log in
          </button>
        )}
      </header>

      {showLogin ? (
        <section className="login-page">
          <button
            className="back-button"
            type="button"
            onClick={() => setShowLogin(false)}
          >
            ← Back to dashboard
          </button>

          <div className="login-card">
            <p className="eyebrow">WELCOME TO HACKCARTEL</p>
            <h1>Member login</h1>
            <p className="login-description">
              Sign in to continue to PSRank.
            </p>

            <form onSubmit={handleLogin}>
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                required
              />

              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
              
              {loginError && <p className="login-error">{loginError}</p>}

              <button className="primary-button submit-button" type="submit" disabled={loading}>
                {loading ? "Signing in..." : "Log in"}
              </button>
            </form>

            <p className="form-note">
              Your HackCartel account will be used to sign in.
            </p>
          </div>
        </section>
      ) : (
        <>
          <section className="welcome" id="dashboard">
            {user && (
              <p className="signed-in-message">
                Signed in as {user.email}
              </p>
            )}
            <p className="eyebrow">HACKCARTEL · PROBLEM STATEMENTS</p>
            <h1>Find the next problem<br />worth solving.</h1>
            <p className="intro">
              Explore the community’s problem statements and see what’s rising to the top.
            </p>
            <button className="primary-button" type="button" onClick={() => {
              document.getElementById("rankings")?.scrollIntoView({ behavior: "smooth" });
            }}>
              Explore rankings <span aria-hidden="true">→</span>
            </button>
          </section>

          <section className="ranking-section" id="rankings">
            <div className="section-heading">
              <div>
                <p className="eyebrow">THE COMMUNITY’S PICKS</p>
                <h2>Top problem statements</h2>
              </div>
              <a className="view-all" href="#rankings">View all →</a>
            </div>

            <div className="empty-state">
              <div className="empty-icon" aria-hidden="true">✳</div>
              <h3>Rankings are getting ready</h3>
              <p>Submitted problem statements will appear here once they’ve been scored.</p>
            </div>
          </section>

          <footer>Made for the HackCartel community</footer>
        </>
      )}
    </main>
  );
}

export default App;