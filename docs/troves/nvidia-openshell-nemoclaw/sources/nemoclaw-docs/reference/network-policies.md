# Network Policies

NemoClaw runs with a strict-by-default network policy. The sandbox can only reach explicitly allowed endpoints. Requests to unlisted destinations are intercepted by OpenShell, and the operator is prompted to approve or deny in real time through the TUI.

## Baseline Policy

Defined in `nemoclaw-blueprint/policies/openclaw-sandbox.yaml`.

### Filesystem

| Path | Access |
| --- | --- |
| `/sandbox`, `/tmp`, `/dev/null` | Read-write |
| `/usr`, `/lib`, `/proc`, `/dev/urandom`, `/app`, `/etc`, `/var/log` | Read-only |

Sandbox process runs as dedicated `sandbox` user and group. Landlock LSM enforcement on best-effort basis.

### Network

Default allowed endpoint groups:

| Policy | Endpoints | Binaries | Rules |
| --- | --- | --- | --- |
| `claude_code` | `api.anthropic.com:443`, `statsig.anthropic.com:443`, `sentry.io:443` | `/usr/local/bin/claude` | All methods |
| `nvidia` | `integrate.api.nvidia.com:443`, `inference-api.nvidia.com:443` | `/usr/local/bin/claude`, `/usr/local/bin/openclaw` | All methods |
| `github` | `github.com:443` | `/usr/bin/gh`, `/usr/bin/git` | All methods, all paths |
| `github_rest_api` | `api.github.com:443` | `/usr/bin/gh` | GET, POST, PATCH, PUT, DELETE |
| `clawhub` | `clawhub.com:443` | `/usr/local/bin/openclaw` | GET, POST |
| `openclaw_api` | `openclaw.ai:443` | `/usr/local/bin/openclaw` | GET, POST |
| `openclaw_docs` | `docs.openclaw.ai:443` | `/usr/local/bin/openclaw` | GET only |
| `npm_registry` | `registry.npmjs.org:443` | `/usr/local/bin/openclaw`, `/usr/local/bin/npm` | GET only |
| `telegram` | `api.telegram.org:443` | Any binary | GET, POST on `/bot*/**` |

All endpoints use TLS termination, enforced at port 443.

### Inference

Baseline allows only `local` inference route. External inference providers reached through OpenShell gateway, not by direct sandbox egress.

## Operator Approval Flow

1. Agent makes network request to unlisted host
2. OpenShell blocks connection and logs attempt
3. TUI (`openshell term`) displays blocked request with host, port, requesting binary
4. Operator approves or denies
5. If approved, endpoint added to running policy for session (not persisted to baseline)

## Modifying the Policy

**Static**: Edit `openclaw-sandbox.yaml` and re-run `nemoclaw onboard`.

**Dynamic**: Apply to running sandbox: `openshell policy set <policy-file>`
