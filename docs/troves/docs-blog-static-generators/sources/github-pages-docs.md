---
source-type: web-page
url: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
fetched: 2026-04-07
title: "Configuring a publishing source for your GitHub Pages site"
---

# Configuring a publishing source for your GitHub Pages site

You can configure your GitHub Pages site to publish when changes are pushed to a specific branch, or you can write a GitHub Actions workflow to publish your site.

## About publishing sources

You can publish your site when changes are pushed to a specific branch, or you can write a GitHub Actions workflow to publish your site.

If you do not need any control over the build process for your site, we recommend that you publish your site when changes are pushed to a specific branch. You can specify which branch and folder to use as your publishing source. The source branch can be any branch in your repository, and the source folder can either be the root of the repository (`/`) on the source branch or a `/docs` folder on the source branch. Whenever changes are pushed to the source branch, the changes in the source folder will be published to your GitHub Pages site.

If you want to use a build process other than Jekyll or you do not want a dedicated branch to hold your compiled static files, we recommend that you write a GitHub Actions workflow to publish your site. GitHub provides workflow templates for common publishing scenarios to help you write your workflow.

## Publishing from a branch

1. Make sure the branch you want to use as your publishing source already exists in your repository.
2. On GitHub, navigate to your site's repository.
3. Under your repository name, click **Settings**.
4. In the "Code and automation" section of the sidebar, click **Pages**.
5. Under "Build and deployment", under "Source", select **Deploy from a branch**.
6. Under "Build and deployment", use the branch dropdown menu and select a publishing source.
7. Optionally, use the folder dropdown menu to select a folder for your publishing source.
8. Click **Save**.

Your GitHub Pages site will always be deployed with a GitHub Actions workflow run, even if you've configured your GitHub Pages site to be built using a different CI tool. Most external CI workflows "deploy" to GitHub Pages by committing the build output to the `gh-pages` branch of the repository, and typically include a `.nojekyll` file.

## Key points for docs/ folder deployment

- GitHub Pages supports publishing from a `/docs` folder on any branch
- You can use the built-in Jekyll build process OR disable it with a `.nojekyll` file
- For custom static site generators, use GitHub Actions workflows
- GitHub provides workflow templates for several static site generators
