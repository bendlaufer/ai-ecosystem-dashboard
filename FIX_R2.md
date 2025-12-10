# Fix Cloudflare R2 Public Development URL

The CORS proxy is timing out on 57MB files. Let's get R2 working properly - it's the best solution.

## Step 1: Verify R2 Configuration

1. **Go to Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Navigate to R2**: Click "R2" → Your bucket `ai-ecosystem-graph`
3. **Check Settings**:
   - Go to **Settings** tab
   - Look for **"Public Development URL"** section
   - It should show: **"Enabled"** with a URL

## Step 2: Re-enable Public Development URL

If it's not working:

1. **Disable** the Public Development URL
2. **Wait 30 seconds**
3. **Enable** it again
4. **Copy the NEW URL** (it might be different from before)

## Step 3: Verify File is Uploaded

1. In your R2 bucket, verify `graph_data.json.gz` is there
2. Check the file size (should be ~57MB)
3. Make sure the filename is exactly `graph_data.json.gz` (case-sensitive)

## Step 4: Test the URL

Try accessing the URL directly in your browser:
```
https://pub-89cf9135be2346638e77c9edf35edf5a.r2.dev/ai-ecosystem-graph/graph_data.json.gz
```

Or if you got a new URL:
```
https://pub-[NEW-ID].r2.dev/ai-ecosystem-graph/graph_data.json.gz
```

## Step 5: Update Code

If you got a new URL, update `index.html`:
1. Find line ~356: `const CDN_URL = 'https://pub-...`
2. Replace with your new URL
3. Commit and push

## Alternative: Use Custom Domain

If public development URL still doesn't work:

1. In R2 Settings → **Custom Domain**
2. Add a custom domain (e.g., `data.yourdomain.com`)
3. Configure DNS as instructed
4. Use that URL instead

## Why R2 is Better

- ✅ No CORS issues (proper CORS headers)
- ✅ Fast CDN performance
- ✅ No file size limits
- ✅ Reliable (no timeouts)
- ✅ Free tier available

The code is already configured to use R2 - we just need to get the public URL working!

