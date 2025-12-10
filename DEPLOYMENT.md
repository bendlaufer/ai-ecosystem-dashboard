# Deployment Guide

## Quick Start: GitHub Pages

Your website is ready to deploy! Follow these steps:

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/bendlaufer/ai-ecosystem-dashboard
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

### Step 2: Access Your Site

After a few minutes, your site will be live at:
**https://bendlaufer.github.io/ai-ecosystem-dashboard/**

### Step 3: Test the Mini Sample

The website comes with a mini sample (`graph_data_mini.json`) that works immediately:
- Open the site
- The default data source is set to "Mini Sample"
- Try searching for a model ID from the mini sample
- Explore the 3D visualization!

## Using the Full Dataset

To use the full 500MB dataset:

1. **Generate the full graph_data.json** locally using the Jupyter notebook
2. **Upload to a CDN or hosting service** (GitHub Pages has a 100MB file limit)
3. **Update the data source URL** in `index.html` to point to your CDN

### Recommended CDN Options:

- **GitHub Releases**: Upload as a release asset (no size limit for releases)
- **AWS S3**: Host the file on S3 with public access
- **Cloudflare R2**: Similar to S3, with free tier
- **Google Cloud Storage**: Another option for large files

### Alternative: Host Locally

You can also host the full dataset on your own server and update the fetch URL in `index.html`.

## Local Testing

Before deploying, test locally:

```bash
# Start a local server
python -m http.server 8000

# Open in browser
open http://localhost:8000
```

## Troubleshooting

### "File not found" errors
- Make sure `graph_data_mini.json` is in the root directory
- Check browser console for specific error messages

### Large file loading issues
- The full dataset (500MB) may take time to load
- Consider implementing lazy loading or pagination
- Use the mini sample for development/testing

### CORS errors
- Make sure you're using a web server (not opening file:// directly)
- GitHub Pages handles CORS automatically

## Next Steps

- Customize the visualization colors and styles
- Add more interactive features
- Implement data caching for better performance
- Add analytics to track usage

