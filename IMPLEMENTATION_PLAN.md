# Component-Based Architecture Implementation Plan

## Step 1: Export Components (Run Once)

```bash
cd "/Users/benjaminlaufer/Python Projects/ai-ecosystem-dashboard"
source venv/bin/activate
python export_components.py
```

This will create:
- `components/component_index.json.gz` (~few MB)
- `components/component_0.json.gz` through `component_N.json.gz`

## Step 2: Upload to R2

Upload the entire `components/` directory to your R2 bucket:
- `ai-ecosystem-graph/components/component_index.json.gz`
- `ai-ecosystem-graph/components/component_0.json.gz`
- etc.

## Step 3: Update Worker

The Worker needs to serve component files:
- `GET /component_index.json.gz` → returns index
- `GET /component_{id}.json.gz` → returns specific component

## Step 4: Update Frontend

Frontend will:
1. Load `component_index.json.gz` on page load (small, fast)
2. When user searches for model, look up `component_id`
3. Load `component_{id}.json.gz` on demand (only what's needed)

## Benefits

- **Before**: Load 570MB file → 5-10 minutes
- **After**: Load index (~2MB) → instant, then load component (~1MB) → < 1 second

## File Sizes

- Index: ~2-5 MB (compressed)
- Average component: ~100KB - 1MB (compressed)
- Largest component: ~10-20MB (compressed)
- Total: Similar to original, but split intelligently

