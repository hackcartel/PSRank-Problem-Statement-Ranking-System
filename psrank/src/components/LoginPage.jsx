import GithubIcon from "./GithubIcon";

function LoginPage({ onSignIn, redirecting }) {
  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-card-icon" aria-hidden="true">✦</div>
        <p className="eyebrow">HACKCARTEL · MEMBER ACCESS</p>
        <h1>Welcome to PSRank</h1>
        <p className="login-description">Sign in to explore and rank community problem statements.</p>
        <button className="github-button" type="button" onClick={onSignIn} disabled={redirecting}>
          <GithubIcon className="github-icon" />
          <span>{redirecting ? "Connecting to GitHub…" : "Sign in or create an account"}</span>
        </button>
        <p className="login-helper">New here? Signing in with GitHub creates your account.</p>
      </section>
    </main>
  );
}

export default LoginPage;
