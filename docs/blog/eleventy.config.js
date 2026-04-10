module.exports = function(eleventyConfig) {
  // Add limit filter for Nunjucks
  eleventyConfig.addFilter("limit", function(arr, limit) {
    return arr.slice(0, limit);
  });
  
  // URL filter for pathPrefix support
  eleventyConfig.addFilter("url", function(path) {
    const pathPrefix = (eleventyConfig.pathPrefix || "/").replace(/\/$/, "");
    if (path.startsWith("http://") || path.startsWith("https://")) {
      return path;
    }
    const cleanPath = path.replace(/^\/+/, "");
    return pathPrefix + "/" + cleanPath;
  });
  
  // Passthrough copy for CSS and assets
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/img");
  
  // Watch CSS files
  eleventyConfig.addWatchTarget("src/css/");
  
  // Filter for date formatting
  eleventyConfig.addFilter("dateFormat", function(date) {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  });
  
  // Filter for RFC3339 date format (for RSS)
  eleventyConfig.addFilter("dateToRfc3339", function(date) {
    return new Date(date).toISOString();
  });
  
  // Filter for getting newest collection item date
  eleventyConfig.addFilter("getNewestCollectionItemDate", function(collection) {
    if (!collection || collection.length === 0) return new Date();
    return collection[0].date;
  });
  
  // Filter for HTML to absolute URLs
  eleventyConfig.addFilter("htmlToAbsoluteUrls", function(html, baseUrl) {
    return html.replace(/href="\//g, `href="${baseUrl}/`);
  });
  
  // Collection for blog posts — only include posts with a published date <= today
  eleventyConfig.addCollection("posts", function(collectionApi) {
    const now = new Date();
    now.setHours(23, 59, 59, 999);
    return collectionApi.getFilteredByTag("post")
      .filter(item => {
        const published = item.data.published;
        if (!published || published === false) return false;
        return new Date(published) <= now;
      })
      .sort((a, b) => {
        // Sort by published date descending (newest first)
        return new Date(b.data.published) - new Date(a.data.published);
      });
  });
  
  // Suppress rendering of posts where published is false
  eleventyConfig.addGlobalData("eleventyComputed", {
    permalink: function(data) {
      if (data.published === false) return false;
      return data.permalink;
    }
  });

  return {
    dir: {
      input: "src",
      output: "dist",
      includes: "_includes",
      layouts: "_layouts"
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    pathPrefix: "/"
  };
};
