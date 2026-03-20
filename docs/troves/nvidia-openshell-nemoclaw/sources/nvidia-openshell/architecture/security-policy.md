# Policy Language

The sandbox system uses a YAML-based policy language to govern sandbox behavior. Policies serve two purposes:

1. **Static configuration** — filesystem access rules, Landlock compatibility, and process privilege dropping (applied once at sandbox startup, immutable).
2. **Dynamic network decisions** — per-connection and per-request access control evaluated at runtime by the OPA engine. Can be updated on a running sandbox via live policy updates.

## Policy Loading

Two paths, selected at startup:

### File Mode (Local Development)

```bash
openshell-sandbox \
  --policy-rules sandbox-policy.rego \
  --policy-data dev-sandbox-policy.yaml \
  -- /bin/bash
```

### gRPC Mode (Production)

```bash
openshell-sandbox \
  --sandbox-id abc123 \
  --openshell-endpoint https://openshell:8080 \
  -- /bin/bash
```

Gateway returns `SandboxPolicy` protobuf message, converted to JSON, validated, expanded, loaded into OPA.

File mode takes precedence if both are provided.

## Live Policy Updates

Available in gRPC mode only. Enables operators to tighten or relax network access rules without restarting:

- Gateway pushes updated policy via gRPC streaming
- OPA engine hot-reloads policy data
- New connections evaluated against updated policy immediately

## Policy Schema

Policies are declarative YAML with sections for:

- **filesystem**: Landlock paths with read/write/execute permissions
- **network**: Per-binary egress rules with host/port/method/path constraints
- **process**: Privilege dropping, seccomp profiles
- **inference**: Model routing rules with credential management
- **L7**: Optional deep packet inspection with TLS MITM for allowed connections
