---
title: "Pre-Commit Security Scanner Landscape"
artifact: SPIKE-015
track: container
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which pre-commit security scanners should swain support beyond gitleaks, and what configuration surface do they need?"
gate: Pre-MVP
risks-addressed:
  - Secrets accidentally committed to repositories
  - Incomplete coverage with a single scanner
linked-artifacts:
  - EPIC-012
trove: ""
---

# Pre-Commit Security Scanner Landscape

## Question

Which pre-commit security scanners should swain support beyond gitleaks, and what configuration surface do they need?

## Go / No-Go Criteria

- **GO:** At least 2 additional scanners identified that cover gaps gitleaks misses (e.g., cloud-specific credential patterns, license compliance, dependency vulnerabilities)
- **NO-GO:** All additional scanners have >80% overlap with gitleaks — stick with gitleaks-only default

## Pivot Recommendation

If no additional scanners add meaningful coverage, simplify the architecture: hardcode gitleaks support in swain-push instead of building a configurable scanner list. Save the abstraction for when there's a real second scanner to support.

## Findings

### Verdict: GO

At least 3 scanners fill distinct gaps that gitleaks does not cover. Gitleaks covers ~160 secret patterns via regex+entropy. TruffleHog adds live credential verification and 800+ detector types. Trivy and OSV-Scanner cover an entirely different domain (dependency vulnerabilities, license compliance, IaC misconfigurations) that gitleaks has zero coverage for. Academic research confirms gitleaks and trufflehog produce 1533 and 438 non-overlapping true positive secrets respectively, proving that even within the "secrets" domain, a single tool leaves gaps.

---

### Tier 1: Secret Scanners (same domain as gitleaks)

#### 1. TruffleHog (trufflesecurity/trufflehog)

| Attribute | Detail |
|-----------|--------|
| **Detects** | 800+ secret types with live credential verification against APIs |
| **Installation** | Go binary. Homebrew (`brew install trufflehog`), curl install script, or Docker image |
| **Pre-commit support** | Native `.pre-commit-hooks.yaml` in repo; also works as raw git hook or via Husky |
| **Stars / Maintenance** | 25k+ stars; actively maintained (Dec 2024 commits, 248 open issues, 139 PRs) |
| **Overlap with gitleaks** | ~40-60% pattern overlap for common secrets (AWS, GitHub, Slack tokens) |
| **Unique coverage** | (a) Live verification — calls actual APIs to confirm credentials are still active, reducing false positives to near zero for verified results. (b) 800+ detectors vs gitleaks' ~160. (c) Scans beyond git: S3 buckets, Docker images, Slack, Jira, Confluence. (d) Identity mapping — traces secrets back to specific service identities |
| **Performance** | Slower than gitleaks on large repos due to verification step. `--results=verified,unknown` flag helps, but expect 2-5x slower than gitleaks for pre-commit |
| **Config surface** | `--only-verified` / `--results=verified,unknown` flag, `--exclude-paths`, custom detector config via YAML |
| **Recommendation** | **INCLUDE (opt-in).** The verification feature is a genuine differentiator — it answers "is this secret still dangerous?" which gitleaks cannot. Not default because of speed penalty |

#### 2. detect-secrets (Yelp/detect-secrets)

| Attribute | Detail |
|-----------|--------|
| **Detects** | 27+ plugins: AWS, Azure, GCP, GitHub, GitLab, Slack, Stripe, Twilio, JWT, NPM, PyPI, OpenAI, private keys, high-entropy strings |
| **Installation** | Python package (`pip install detect-secrets`). Requires Python runtime |
| **Pre-commit support** | Native `.pre-commit-hooks.yaml`; baseline-driven workflow (`--baseline .secrets.baseline`) |
| **Stars / Maintenance** | 4.4k stars; actively maintained (Jan 2025 commits, 92 open issues) |
| **Overlap with gitleaks** | ~70% overlap for common patterns |
| **Unique coverage** | (a) Baseline model — tracks known secrets and only flags new ones, ideal for brownfield repos. (b) Plugin architecture allows custom detectors. (c) `audit` workflow for team review of baselines |
| **Performance** | Moderate; Python startup overhead but scans only staged files in pre-commit mode |
| **Config surface** | `.secrets.baseline` file, plugin enable/disable, custom regex plugins, `--exclude-files`, `--exclude-lines` |
| **Recommendation** | **EXCLUDE from default set.** High overlap with gitleaks, Python dependency adds weight. The baseline model is valuable but gitleaks' `.gitleaksignore` covers similar ground. Better suited for enterprise teams than for swain's lightweight profile |

#### 3. Talisman (thoughtworks/talisman)

| Attribute | Detail |
|-----------|--------|
| **Detects** | Tokens, passwords, private keys, base64/hex encoded values, large files, credit card numbers, suspicious filenames |
| **Installation** | Go binary. Install script, Homebrew, or pre-commit framework |
| **Pre-commit support** | Native `.pre-commit-hooks.yaml`; also installs as global hook via `talisman --install-hook` |
| **Stars / Maintenance** | 2.1k stars; actively maintained (v1.36.0, 31 open issues) |
| **Overlap with gitleaks** | ~75% overlap |
| **Unique coverage** | (a) File-size and filename pattern detection (catches accidental key file commits). (b) Checksum-based ignoring. (c) Global hook install — one command protects all repos |
| **Performance** | Fast (Go binary), comparable to gitleaks |
| **Config surface** | `.talismanrc` YAML file for ignores, custom patterns, file size thresholds |
| **Recommendation** | **EXCLUDE.** Too much overlap with gitleaks. The filename/filesize checks are nice but not enough to justify a second secret scanner |

#### 4. secretlint (secretlint/secretlint)

| Attribute | Detail |
|-----------|--------|
| **Detects** | SSH keys, AWS, GCP, Slack, npm tokens, Anthropic/Claude API keys, database connection strings, private keys |
| **Installation** | npm package (`npm install secretlint`). Requires Node.js runtime. Also Docker image |
| **Pre-commit support** | Via Husky/lint-staged (Node projects) or Docker-based pre-commit hook |
| **Stars / Maintenance** | 1.3k stars; actively maintained (v11.3.1, Feb 2026 updates, new Anthropic rule) |
| **Overlap with gitleaks** | ~65% overlap |
| **Unique coverage** | (a) Plugin for Anthropic/Claude API keys (relevant for AI-heavy projects). (b) Database connection string detection. (c) Pluggable rule architecture for custom rules |
| **Performance** | Moderate; Node.js startup overhead |
| **Config surface** | `.secretlintrc.json` with per-rule enable/disable and options |
| **Recommendation** | **EXCLUDE.** Node.js dependency, moderate overlap with gitleaks. The Anthropic key detection is interesting but could be added as a custom gitleaks rule |

#### 5. git-secrets (awslabs/git-secrets)

| Attribute | Detail |
|-----------|--------|
| **Detects** | AWS credentials, custom regex patterns |
| **Installation** | Bash script. Homebrew or manual install |
| **Pre-commit support** | Native git hook (`git secrets --install`) |
| **Stars / Maintenance** | 13.2k stars but **last commit May 2020 — effectively abandoned** |
| **Overlap with gitleaks** | ~95% overlap (AWS patterns are well covered by gitleaks) |
| **Recommendation** | **EXCLUDE.** Unmaintained since 2020. All its AWS patterns are covered by gitleaks |

#### 6. ripsecrets (sirwart/ripsecrets)

| Attribute | Detail |
|-----------|--------|
| **Detects** | High-entropy strings using probability theory, generic secret patterns |
| **Installation** | Rust binary. Homebrew, cargo, or prebuilt binaries |
| **Pre-commit support** | Native `.pre-commit-hooks.yaml` |
| **Stars / Maintenance** | Moderate activity; v0.1.11 on Cargo |
| **Overlap with gitleaks** | ~80% overlap (entropy-focused, similar to gitleaks' entropy mode) |
| **Unique coverage** | Extremely fast (95x faster than some tools per benchmarks). Purely local, no network calls |
| **Recommendation** | **EXCLUDE.** Speed is impressive but gitleaks is already fast enough for pre-commit. High overlap, no unique detection categories |

---

### Tier 2: Beyond Secrets (different domains)

#### 7. Trivy (aquasecurity/trivy)

| Attribute | Detail |
|-----------|--------|
| **Detects** | Dependency vulnerabilities (CVEs), license compliance violations, IaC misconfigurations (Terraform, CloudFormation, Kubernetes, Helm), secrets (bonus), container image vulnerabilities |
| **Installation** | Go binary. Homebrew, apt, yum, or Docker image |
| **Pre-commit support** | Community hooks (cebidhem/pre-commit-trivy, mxab/pre-commit-trivy). Not official but functional |
| **Stars / Maintenance** | Very actively maintained by Aqua Security. Major "Next-Gen Trivy" planned for 2026 |
| **Overlap with gitleaks** | ~5% (some basic secret detection, but primary value is entirely different domain) |
| **Unique coverage** | (a) Dependency vulnerability scanning (CVEs in package.json, go.mod, requirements.txt, etc.). (b) License compliance (detect GPL, AGPL in dependencies). (c) IaC misconfiguration detection. (d) Filesystem scanning mode works perfectly for pre-commit |
| **Performance** | First run downloads vulnerability DB (~100MB). Subsequent runs fast with local cache. `--skip-db-update` flag for offline/fast mode |
| **Config surface** | `trivy.yaml` config file, `--severity` threshold, `--scanners` selector (vuln, misconfig, secret, license), `--skip-dirs`, `.trivyignore` for suppressions |
| **Recommendation** | **INCLUDE (opt-in).** Covers an entirely different domain than gitleaks — dependency vulnerabilities and license compliance are real risks that no secret scanner addresses. Pre-commit integration works via `trivy fs` mode |

#### 8. OSV-Scanner (google/osv-scanner)

| Attribute | Detail |
|-----------|--------|
| **Detects** | Dependency vulnerabilities using the OSV database (aggregates NVD, GitHub Advisories, RustSec, Go vulndb, PyPI advisories, etc.) |
| **Installation** | Go binary. `go install`, prebuilt binaries, or Docker |
| **Pre-commit support** | Official `.pre-commit-hooks.yaml` in repo (v2.2.4+) |
| **Stars / Maintenance** | Actively maintained by Google/OpenSSF. Regular releases |
| **Overlap with gitleaks** | 0% (completely different domain) |
| **Unique coverage** | (a) Broadest vulnerability database coverage (aggregates 15+ advisory sources). (b) Lightweight and fast — no large DB download like Trivy. (c) Guided remediation suggestions. (d) Official pre-commit support |
| **Performance** | Fast. Queries OSV API (requires network) but lightweight |
| **Config surface** | `osv-scanner.toml` config file, `--format`, `--verbosity`, ignore rules per vulnerability ID |
| **Recommendation** | **INCLUDE (opt-in).** Lighter than Trivy for pure dependency vulnerability scanning. Better ecosystem coverage than Trivy for some languages. Good alternative when you want vuln scanning without Trivy's full weight |

#### 9. Checkov (bridgecrewio/checkov)

| Attribute | Detail |
|-----------|--------|
| **Detects** | IaC misconfigurations (Terraform, CloudFormation, Kubernetes, ARM, Serverless), supply chain issues, license compliance, 750+ built-in policies (CIS, PCI, HIPAA) |
| **Installation** | Python package (`pip install checkov`). Also Docker image |
| **Pre-commit support** | Official `.pre-commit-hooks.yaml`; documented at checkov.io |
| **Stars / Maintenance** | Actively maintained by Bridgecrew/Palo Alto Networks |
| **Overlap with gitleaks** | 0% (completely different domain) |
| **Unique coverage** | (a) Deepest IaC policy library. (b) Compliance framework mapping (CIS, PCI, HIPAA). (c) Supply chain and license compliance |
| **Config surface** | `.checkov.yaml`, `--check` / `--skip-check` for individual policies, `--framework` selector |
| **Recommendation** | **OPTIONAL (IaC projects only).** Only relevant for projects with Terraform/CloudFormation/Kubernetes configs. Python dependency. Not a good default for swain's general-purpose profile |

---

### Summary Matrix

| Tool | Domain | Overlap w/ gitleaks | Installation | Pre-commit | Maintained | Recommendation |
|------|--------|-------------------|--------------|------------|------------|----------------|
| **gitleaks** | Secrets | — (baseline) | Go binary | Native | Yes | DEFAULT |
| **TruffleHog** | Secrets + verification | 40-60% | Go binary | Native | Yes | **INCLUDE (opt-in)** |
| **Trivy** | Vulns + License + IaC | ~5% | Go binary | Community | Yes | **INCLUDE (opt-in)** |
| **OSV-Scanner** | Dependency vulns | 0% | Go binary | Official | Yes | **INCLUDE (opt-in)** |
| detect-secrets | Secrets | ~70% | Python | Native | Yes | Exclude |
| Talisman | Secrets | ~75% | Go binary | Native | Yes | Exclude |
| secretlint | Secrets | ~65% | Node.js | Via Husky/Docker | Yes | Exclude |
| git-secrets | Secrets (AWS) | ~95% | Bash | Native | **No (2020)** | Exclude |
| ripsecrets | Secrets (entropy) | ~80% | Rust binary | Native | Moderate | Exclude |
| Checkov | IaC + compliance | 0% | Python | Official | Yes | Optional (IaC only) |

---

### Configuration Surface for Recommended Scanners

Swain needs to expose these configuration knobs per scanner:

**Gitleaks (default):**
- `.gitleaks.toml` — custom rules, allowlists
- `.gitleaksignore` — known secret suppressions
- swain config: enable/disable (default: enabled)

**TruffleHog (opt-in):**
- `--results=verified,unknown` vs `--only-verified` — verification strictness
- `--exclude-paths` — path exclusions
- swain config: enable/disable, verification mode (verified-only vs all)

**Trivy (opt-in):**
- `trivy.yaml` — scanner selection, severity threshold
- `.trivyignore` — vulnerability suppressions
- `--scanners` — which scanners to run (vuln, misconfig, secret, license)
- swain config: enable/disable, severity threshold, scanner types

**OSV-Scanner (opt-in):**
- `osv-scanner.toml` — ignore rules, format
- swain config: enable/disable

**Swain integration model:**
```yaml
# .swain/push.yaml (proposed)
scanners:
  gitleaks:
    enabled: true          # default
  trufflehog:
    enabled: false         # opt-in
    verify: true           # only report verified secrets
  trivy:
    enabled: false         # opt-in
    scanners: [vuln, license]
    severity: HIGH,CRITICAL
  osv-scanner:
    enabled: false         # opt-in
```

All recommended scanners are Go binaries (except Checkov), meaning no Python/Node.js runtime dependencies for the core set. This aligns well with swain's "vendored single binary" philosophy.

---

### Architectural Recommendation

Build a **scanner adapter interface** in swain-push rather than hardcoding gitleaks. The interface needs:

1. `check_installed()` — verify the scanner binary is available
2. `run_scan(staged_files)` — execute the scan on staged files
3. `parse_results()` — normalize output to a common findings format
4. `get_config_path()` — locate scanner-specific config files

This abstraction is justified because we have 3 confirmed scanners with distinct coverage domains (secrets, dependency vulns, license compliance). The adapter pattern lets users mix and match without swain needing to understand each tool's output format.

---

### Sources

- [TruffleHog vs Gitleaks Comparison (Jit)](https://www.jit.io/resources/appsec-tools/trufflehog-vs-gitleaks-a-detailed-comparison-of-secret-scanning-tools)
- [Best Secret Scanning Tools in 2025 (Aikido)](https://www.aikido.dev/blog/top-secret-scanning-tools)
- [Top 8 Git Secrets Scanners in 2026 (Jit)](https://www.jit.io/resources/appsec-tools/git-secrets-scanners-key-features-and-top-tools-)
- [TruffleHog Pre-commit Docs](https://docs.trufflesecurity.com/pre-commit-hooks)
- [TruffleHog GitHub](https://github.com/trufflesecurity/trufflehog)
- [detect-secrets GitHub (Yelp)](https://github.com/Yelp/detect-secrets)
- [Talisman GitHub (ThoughtWorks)](https://github.com/thoughtworks/talisman)
- [secretlint GitHub](https://github.com/secretlint/secretlint)
- [git-secrets GitHub (AWS Labs)](https://github.com/awslabs/git-secrets)
- [OSV-Scanner GitHub (Google)](https://github.com/google/osv-scanner)
- [Trivy (Aqua Security)](https://trivy.dev/)
- [Checkov Pre-commit Docs](https://www.checkov.io/4.Integrations/pre-commit.html)
- [pre-commit-trivy Community Hook](https://github.com/cebidhem/pre-commit-trivy)
- [ripsecrets GitHub](https://github.com/sirwart/ripsecrets)
- [How TruffleHog Verifies Secrets](https://trufflesecurity.com/blog/how-trufflehog-verifies-secrets)
- [Comparative Study of Secrets Reporting by Detection Tools (arXiv)](https://arxiv.org/pdf/2307.00714)
- [Gitleaks Rule System (DeepWiki)](https://deepwiki.com/gitleaks/gitleaks/4-rule-system)
- [Nosey Parker GitHub (Praetorian)](https://github.com/praetorian-inc/noseyparker)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 7b39e3e | Initial creation |
| Active | 2026-03-13 | — | Research conducted: 10 tools evaluated across 3 domains |
| Complete | 2026-03-13 | 474f2be | GO: 3 scanners fill gitleaks gaps |
