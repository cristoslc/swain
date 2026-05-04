# Docs Folder Blog Generators — Research Synthesis

## Key findings

### GitHub Pages supports `/docs` folder publishing natively

GitHub Pages can publish from a `/docs` folder on any branch without requiring GitHub Actions. You simply:
1. Go to Settings → Pages
2. Select "Deploy from a branch"
3. Choose your branch and `/docs` folder
4. Click Save

This works with **any static site generator** — just add a `.nojekyll` file to disable Jekyll's built-in build process [github-pages-docs].

### Astro is modern but may be overkill for simple blogs

Astro offers:
- Zero JavaScript by default (66% of Astro sites pass Core Web Vitals)
- Content Collections for type-safe Markdown
- Built-in blog themes (Stablo, Microblog, Dante, OpenBlog)
- React/Vue/Svelte/Preact/Solid integration support

However, Astro requires Node.js and a build step. Best for content-driven sites where you want modern features like View Transitions and optimized images [astro-overview][ssg-comparison-2025].

### Hugo is the speed champion

Hugo consistently ranks as the fastest SSG:
- Written in Go, builds sites in milliseconds
- 87k+ GitHub stars (largest community)
- Single binary installation (no Node.js dependencies)
- Built-in image processing, Sass, JavaScript bundling
- Embedded dev server with live reload

Hugo outputs to a `public/` folder by default, but you can configure it to output to `docs/` for GitHub Pages deployment [hugo-overview][ssg-comparison-2025].

### Eleventy (11ty) is the simplest full-featured option

Eleventy prioritizes simplicity:
- No client-side JavaScript required
- Choose your template language (Markdown, Liquid, Nunjucks, Handlebars, etc.)
- 17.4M downloads, active community
- Recently rebranded to "Build Awesome" (March 2026)
- v3.1.0 is 11% faster and 22% smaller

Eleventy can output to any directory, making `docs/` deployment straightforward [eleventy-overview][ssg-comparison-2025].

### Minimalist alternatives exist

If "set-and-forget" is the priority, consider ultra-simple options:

- **BashBlog**: A single Bash script to create blogs — "probably the simplest static site generator in the world"
- **MMSSG**: Most Minimal Static Site Generator (Go-based) — outputs directly to `docs/` folder, ~30 minutes to customize
- **Hexo**: Node.js-based, designed specifically for blogging
- **Pelican**: Python-based, prioritizes chronological content (blog posts) [minimal-ssg-options]

## Points of agreement

### All sources agree on these criteria for "set-and-forget" blogs:

1. **No build dependencies on deployment** — Generate locally, push to `docs/`, GitHub Pages serves it
2. **Markdown support** — Write posts in plain text
3. **RSS/Atom feed** — Automatic feed generation for blog readers
4. **Theme/customization** — Either built-in themes or easy templating
5. **Fast local dev server** — See changes instantly before pushing

### GitHub Pages deployment patterns

Two approaches work for `docs/` folder blogs:

**Option A: Branch folder deployment** (simplest)
- Generate site locally to `docs/` folder
- Commit and push to trunk branch
- GitHub Pages serves from `docs/`

**Option B: GitHub Actions workflow** (automated)
- Configure GitHub Actions to build on push
- Deploy to GitHub Pages automatically
- More control over build environment

## Points of disagreement

### Build complexity vs. features

| Generator | Build complexity | Features | Best for |
|-----------|-----------------|----------|----------|
| BashBlog/MMSSG | Minimal | Basic blog | Personal blogs, minimalists |
| Eleventy | Low | Flexible templating | Content sites, simplicity |
| Hugo | Low-Medium | Full-featured | Large sites, speed |
| Astro | Medium | Modern features | Content marketing, portfolios |
| Next.js | High | Hybrid static/dynamic | Apps needing server features |

Sources differ on whether the extra features of Astro/Next.js justify the complexity for a simple blog [ssg-comparison-2025][minimal-ssg-options].

### Node.js dependency

Some sources recommend avoiding Node.js-based generators (Astro, Eleventy, Hexo) for long-term stability, preferring single-binary solutions like Hugo (Go) or Zola (Rust) that don't require package management [hugo-overview][minimal-ssg-options].

Other sources argue Node.js is ubiquitous enough that dependency concerns are overstated [astro-overview][eleventy-overview].

## Gaps

### What this research doesn't cover:

1. **Migration path from Astro** — If you already have an Astro blog, what's the effort to move to Hugo/Eleventy?
2. **Specific theme recommendations** — Which Hugo/Eleventy themes work best for technical blogs?
3. **Custom domain setup** — How to configure custom domains with `docs/` folder deployment?
4. **Search functionality** — Which generators have the best built-in search for blog archives?
5. **Comment systems** — Integration with Disqus, Giscus, or other comment platforms

## Recommendations by use case

### "I just want to write" (minimal setup)
→ **BashBlog** or **MMSSG** — Both output to `docs/` folder, minimal configuration

### "I want simplicity with room to grow" (balanced)
→ **Eleventy** — Simple start, extensive plugin ecosystem if you need more later

### "I want the fastest builds" (performance)
→ **Hugo** — Unmatched build speed, mature ecosystem, huge theme library

### "I already know React/Node" (familiarity)
→ **Astro** — Modern DX, zero JS by default, familiar tooling

### "I'm already using Astro" (migration question)
→ **Stay with Astro** — The complexity difference may not justify migration effort for a working blog

## Next steps

To make a decision, consider:
1. How much time do you want to spend on setup vs. writing?
2. Do you need features like image optimization, view transitions, or UI framework integration?
3. Are you comfortable with Node.js tooling, or do you prefer single-binary tools?
4. Is your existing Astro blog working well, or are you actively frustrated with it?
