# Network Policies

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

Network policies control what external resources a sandbox can access through a host-side HTTP/HTTPS filtering proxy.

## Purpose

The page positions network policies as a way to:

- prevent access to internal networks
- enforce compliance or egress restrictions
- limit agents to specific public services

The docs are explicit that network policies are only one layer of defense. The microVM boundary remains the primary isolation mechanism.

## Traffic model

Each sandbox routes outbound HTTP and HTTPS traffic through a filtering proxy exposed inside the sandbox as:

```text
host.docker.internal:3128
```

Other external protocols such as raw TCP and UDP are blocked.

When a request goes through the proxy, the page says the proxy:

1. checks host-based policy rules
2. connects only if the host is permitted
3. applies CIDR checks to destinations that are not explicitly allow-listed

The page calls out a special case: `host.docker.internal` is rewritten to `localhost`, so allow-rules should be written against `localhost` rather than `host.docker.internal`.

## Security considerations

The docs warn that:

- broad allow-rules on domains like `github.com` allow access to all content on those domains
- domain fronting can bypass some filter assumptions
- filters restrict destination hosts, not content semantics

The recommendation is to allow only domains the operator explicitly trusts with project data.

## Default policy

New sandboxes default to an `allow` policy that blocks sensitive network ranges while still allowing internet access.

Blocked CIDRs documented on the page:

- `10.0.0.0/8`
- `127.0.0.0/8`
- `169.254.0.0/16`
- `172.16.0.0/12`
- `192.168.0.0/16`
- `::1/128`
- `fc00::/7`
- `fe80::/10`

Explicit default allow-hosts:

- `*.anthropic.com`
- `platform.claude.com:443`

The stated goal is to block private networks, localhost, and metadata-style targets while preserving ordinary internet connectivity.

## Monitoring

The docs provide a built-in network log command:

```console
$ docker sandbox network log
```

The log summarizes allowed and blocked HTTP/HTTPS requests and includes:

- sandbox name
- destination host and port
- matched rule
- last seen timestamp
- request count

This is presented as the main feedback loop for tuning policy rules.

## Applying policies

Policy changes are applied to a running sandbox and take effect immediately:

```console
$ docker sandbox network proxy my-sandbox ...
```

The page shows several common patterns.

### Block internal networks

```console
$ docker sandbox network proxy my-sandbox \
  --policy allow \
  --block-cidr 10.0.0.0/8 \
  --block-cidr 172.16.0.0/12 \
  --block-cidr 192.168.0.0/16 \
  --block-cidr 127.0.0.0/8
```

### Allow package managers only

```console
$ docker sandbox network proxy my-sandbox \
  --policy deny \
  --allow-host "*.npmjs.org" \
  --allow-host "*.pypi.org" \
  --allow-host "files.pythonhosted.org" \
  --allow-host "*.rubygems.org" \
  --allow-host github.com
```

### Allow AI APIs and development infrastructure

```console
$ docker sandbox network proxy my-sandbox \
  --policy deny \
  --allow-host api.anthropic.com \
  --allow-host "*.npmjs.org" \
  --allow-host "*.pypi.org" \
  --allow-host github.com \
  --allow-host "*.githubusercontent.com"
```

The examples reinforce that the operator must include whatever hosts the selected agent backend actually needs.
