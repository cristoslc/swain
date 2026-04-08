module.exports = function(eleventyConfig) {
  // Add limit filter for Nunjucks
  eleventyConfig.addFilter("limit", function(arr, limit) {
    return arr.slice(0, limit);
  });
  
  // Passthrough copy for CSS and assets
  eleventyConfig.addPassthroughCopy("src/css");
  
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
  
  // Collection for blog posts
  eleventyConfig.addCollection("posts", function(collectionApi) {
    return collectionApi.getFilteredByTag("post").reverse();
  });
  
  return {
    dir: {
      input: "src",
      output: "docs",
      includes: "_includes",
      layouts: "_layouts"
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};
