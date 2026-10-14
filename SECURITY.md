# Credentials and local development

Keep runtime credentials in the environment or a secret manager. Never commit
real values to example files, source code, Dockerfiles, logs, generated config,
or files served by the web server. Use dummy credentials for tests.

Install [Gitleaks](https://github.com/gitleaks/gitleaks), then enable the local
commit guard in each clone:

```sh
git config core.hooksPath .githooks
```

The guard checks staged changes and refuses commits if the scanner is missing
or detects a secret. Run a full check when reviewing existing code:

```sh
gitleaks dir --redact=100 .
gitleaks git --log-opts="--all" --redact=100 .
```

Removing a value in a new commit does not remove previous commits. If a secret
was exposed, revoke or rotate it at its provider and update affected deployments.
Coordinate any history rewrite with repository collaborators before publishing it.
Do not put secret values into issues, pull requests, or commit messages.

This is a sanitized snapshot of a legacy project for source review. It does not include operational data or credentials. A clean credential scan is not a full application security audit. Review dependencies and deployment settings before running a public service.
