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

## ⚠️ Important: CORS Issue with GitHub Releases

**The Problem**: When you access a GitHub Releases file directly in a browser, it downloads the file instead of displaying it. More importantly, GitHub Releases may not include CORS (Cross-Origin Resource Sharing) headers, which means `fetch()` requests from your website may fail with CORS errors.

**The Solution**: You have several options:

### Option 1: Use a CORS Proxy (Quick Fix)

Use a free CORS proxy service to access the GitHub Releases file:

1. Update `index.html` (around line 340):
   ```javascript
   // Use CORS proxy
   const CDN_URL = 'https://api.allorigins.win/raw?url=' + 
       encodeURIComponent('https://github.com/bendlaufer/ai-ecosystem-dashboard/releases/download/v1.0/graph_data.json');
   ```

**Pros**: Quick, free, no setup  
**Cons**: Third-party dependency, may have rate limits, slower

### Option 2: Use a Proper CDN (Recommended for Production)

Host the file on a CDN that supports CORS:

- **Cloudflare R2** (Recommended - free tier available)
- **AWS S3 + CloudFront**
- **Google Cloud Storage**
- **Vercel Blob Storage**

See "Alternative CDN Options" section below for details.

### Option 3: Test GitHub Releases First

Try the direct GitHub Releases URL first. If it works, great! If you get CORS errors in the browser console, use Option 1 or 2.

## Step 2: Update index.html with CDN URL

After creating the release, update the CDN URL in `index.html`:

1. Open `index.html`
2. Find the `CDN_URL` constant (around line 340)
3. Choose one of the options above
4. Update the URL with your release tag version
5. Save the file

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

## Alternative CDN Options (Recommended for Production)

For production use, consider these CDN options that properly support CORS:

### Cloudflare R2 (Recommended)

1. **Sign up**: https://dash.cloudflare.com (free tier: 10GB storage, 1M requests/month)
2. **Create a bucket**: R2 → Create bucket
3. **Upload file**: Upload `graph_data.json` to the bucket
4. **Enable public access**: 
   - Go to bucket settings
   - Enable "Public Access"
   - Copy the public URL
5. **Update CDN_URL in index.html**:
   ```javascript
   const CDN_URL = 'https://your-bucket.r2.dev/graph_data.json';
   ```

**Pros**: Free tier, fast, proper CORS support, no file size limits  
**Cons**: Requires Cloudflare account

### AWS S3 + CloudFront

1. **Create S3 bucket**: AWS Console → S3 → Create bucket
2. **Upload file**: Upload `graph_data.json`
3. **Enable public access**: Bucket permissions → Public access
4. **Set CORS**: Bucket permissions → CORS configuration:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```
5. **Use S3 URL or CloudFront**:
   ```javascript
   const CDN_URL = 'https://your-bucket.s3.amazonaws.com/graph_data.json';
   ```

**Pros**: Reliable, scalable  
**Cons**: Costs money (though minimal for static hosting)

### Google Cloud Storage

1. **Create bucket**: GCS Console → Create bucket
2. **Upload file**: Upload `graph_data.json`
3. **Make public**: Bucket permissions → Add public access
4. **Use public URL**:
   ```javascript
   const CDN_URL = 'https://storage.googleapis.com/your-bucket/graph_data.json';
   ```

**Pros**: Reliable, good performance  
**Cons**: Costs money

### jsDelivr (Not Recommended - Size Limit)

- GitHub Releases files can be accessed via jsDelivr:
- `https://cdn.jsdelivr.net/gh/bendlaufer/ai-ecosystem-dashboard@v1.0/graph_data.json`
- **Note**: jsDelivr has a 50MB limit, so this **won't work** for 500MB files

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

