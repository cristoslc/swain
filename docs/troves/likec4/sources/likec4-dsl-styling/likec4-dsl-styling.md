---
source-id: "likec4-dsl-styling"
title: "LikeC4 Styling Guide"
type: documentation-site
url: "https://likec4.dev/dsl/styling/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 Styling Guide

## Element Styling Levels

1. **Kind-level** in specification (applies to all elements of that kind)
2. **Individual element** in model or deployment (overrides kind styles)
3. **Per-view** customization (view-specific overrides)

## Shape Properties

Available shapes: `rectangle` (default), `component`, `storage`, `cylinder`, `browser`, `mobile`, `person`, `queue`, `bucket`, `document`.

## Color Options

Built-in: `primary` (default), `secondary`, `muted`, `amber`, `gray`, `green`, `indigo`, `red`.

Custom colors can be defined in the specification section.

## Size Properties

| Property | Purpose |
|----------|---------|
| `size` | Shape dimensions |
| `padding` | Space around title |
| `textSize` | Font size of title |

Values: `xsmall`/`xs`, `small`/`sm`, `medium`/`md` (default), `large`/`lg`, `xlarge`/`xl`.

## Container Styling

- **opacity**: Transparency (e.g., `10%`)
- **border**: `dashed` (default), `dotted`, `solid`, `none`
- **multiple**: `true` to display multiple instances

## Icon Sources

- **External URLs**: `https://icons.terrastruct.com/dev%2Fpostgresql.svg`
- **Local files**: `../postgresql.svg`
- **Bundled icon packs**:
  - `aws:` — AWS architecture icons
  - `azure:` — Microsoft Azure icons
  - `bootstrap:` — Bootstrap Icons (2,000+)
  - `gcp:` — Google Cloud Platform icons
  - `tech:` — Technology icons

Icon customization: `iconColor`, `iconSize`, `iconPosition` (`left`, `right`, `top`, `bottom`).

## Relationship Styling

### Line Styles

`dashed` (default), `solid`, `dotted`.

### Arrow Types

| Type | Description |
|------|-------------|
| `normal` | Standard arrow (default head) |
| `onormal` | Outlined arrow (unfilled) |
| `diamond` | Diamond-shaped arrow |
| `odiamond` | Outlined diamond |
| `crow` | Crow's foot notation |
| `vee` | Vee-shaped arrow |
| `open` | Open arrow |
| `none` | No arrow (default tail) |

```likec4
model {
  customer -> ui 'opens in browser' {
    style {
      head diamond
      tail crow
      line solid
      color amber
    }
  }
}
```
