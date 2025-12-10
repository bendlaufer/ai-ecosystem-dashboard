# Component-Based Architecture

## Overview

Instead of loading a 570MB JSON file, we now split the graph into connected components and only load what's needed.

## File Structure

```
components/
├── component_index.json.gz      # Small index file (~few MB)
├── component_0.json.gz          # Component 0 (could be large)
├── component_1.json.gz          # Component 1
├── component_2.json.gz          # Component 2
└── ...
```

## Index File Structure

```json
{
  "component_index": {
    "model_id_1": 0,
    "model_id_2": 0,
    "model_id_3": 1,
    ...
  },
  "component_stats": [
    {
      "component_id": 0,
      "nodes": 1042,
      "edges": 1041,
      "file_size_mb": 0.36,
      "sample_models": ["zera09/SmolVLM", ...]
    },
    ...
  ],
  "total_components": 12345,
  "total_nodes": 1860411,
  "total_edges": 533295
}
```

## Benefits

1. **Fast Loading**: Only load the component you need (typically < 1MB vs 570MB)
2. **Better UX**: Instant loading instead of minutes
3. **Scalable**: Works even if graph grows to millions of nodes
4. **Efficient**: No need to decompress entire graph

## Workflow

1. **User searches for model** (e.g., "zera09/SmolVLM")
2. **Load index** (~few MB, cached)
3. **Look up component_id** from index
4. **Load only that component** (~few hundred KB to few MB)
5. **Display visualization**

## Implementation Steps

1. Run `export_components.py` to create component files
2. Upload `components/` directory to R2 bucket
3. Update frontend to:
   - Load `component_index.json.gz` on page load
   - When user searches, look up component_id
   - Load `component_{id}.json.gz` on demand
4. Update Worker to serve component files

