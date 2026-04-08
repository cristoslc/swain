#!/bin/bash
# Build blog when source files change

echo "Building blog..."

# Navigate to blog directory
cd "$(dirname "$0")" || exit 1

# Build the blog
npm run build

# Check if build succeeded
if [ $? -ne 0 ]; then
  echo "ERROR: Blog build failed!"
  exit 1
fi

# Stage the built output
git add docs/

echo "Blog built successfully!"
exit 0
