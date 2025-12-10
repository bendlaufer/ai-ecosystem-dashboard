# CDN Setup Guide for Full Dataset

This guide will help you upload the 500MB `graph_data.json` file to GitHub Releases so it can be accessed via CDN.

## Step 1: Create a GitHub Release

### Option A: Using GitHub Web Interface (Recommended)

1. **Go to your repository**: https://github.com/bendlaufer/ai-ecosystem-dashboard

2. **Click on "Releases"** (right sidebar, or go to: https://github.com/bendlaufer/ai-ecosystem-dashboard/releases)

3. **Click "Create a new release"** (or "Draft a new release")

4. **Fill in the release form**:
   - **Tag version**: `v1.0` (or any version number like `v1.0.0`)
   - **Release title**: `Full Dataset Release` (or any title)
   - **Description**: 
     ```
     Full AI ecosystem graph dataset (500MB)
     Contains 1.8M+ nodes and 533K+ edges
     ```
   - **Target**: Select `main` branch

5. **Attach the file**:
   - Scroll down to "Attach binaries by dropping them here or selecting them"
   - Drag and drop `graph_data.json` OR click to browse and select it
   - **Important**: The file is 569MB, so upload may take several minutes

6. **Click "Publish release"**

7. **Copy the download URL**:
   - After publishing, the file will be available at:
   - `https://github.com/bendlaufer/ai-ecosystem-dashboard/releases/download/v1.0/graph_data.json`
   - (Replace `v1.0` with your actual tag version)

### Option B: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI first (if not installed)
# brew install gh  # on macOS

# Authenticate
gh auth login

# Create release and upload file
gh release create v1.0 \
  --title "Full Dataset Release" \
  --notes "Full AI ecosystem graph dataset (500MB)" \
  graph_data.json
```

## Step 2: Update index.html with CDN URL

After creating the release, update the CDN URL in `index.html`:

1. Open `index.html`
2. Find this line (around line 340):
   ```javascript
   const CDN_URL = 'https://github.com/bendlaufer/ai-ecosystem-dashboard/releases/download/v1.0/graph_data.json';
   ```
3. Replace `v1.0` with your actual release tag version if different
4. Save the file

## Step 3: Test the CDN URL

1. **Verify the URL works**:
   ```bash
   curl -I https://github.com/bendlaufer/ai-ecosystem-dashboard/releases/download/v1.0/graph_data.json
   ```
   Should return `200 OK`

2. **Test in browser**:
   - Open your local server: http://localhost:8000
   - Select "Full Dataset - CDN (500MB) ⚡" from the dropdown
   - The file should load (may take a minute for 500MB)

## Step 4: Commit and Push

```bash
git add index.html
git commit -m "Add CDN support for full dataset"
git push
```

## Alternative CDN Options

If GitHub Releases doesn't work for you, here are other options:

### AWS S3 + CloudFront
- Upload to S3 bucket
- Enable public access
- Use S3 URL or CloudFront distribution URL

### Cloudflare R2
- Similar to S3
- Free tier available
- Good performance

### Google Cloud Storage
- Upload to GCS bucket
- Make it publicly accessible
- Use the public URL

### jsDelivr (for GitHub Releases)
- GitHub Releases files can be accessed via jsDelivr:
- `https://cdn.jsdelivr.net/gh/bendlaufer/ai-ecosystem-dashboard@v1.0/graph_data.json`
- (Note: jsDelivr has a 50MB limit, so this won't work for 500MB files)

## Troubleshooting

### "File too large" error
- GitHub Releases supports files up to 2GB, so 569MB should be fine
- If you get errors, try uploading in smaller chunks or use a different CDN

### CORS errors
- GitHub Releases should handle CORS automatically
- If you use a different CDN, make sure CORS is enabled

### Slow loading
- 500MB file will take time to download
- Consider adding a progress indicator
- Consider implementing lazy loading or streaming

### Update the CDN URL
- If you create a new release with a different version, update the `CDN_URL` constant in `index.html`

