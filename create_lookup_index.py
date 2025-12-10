"""
Create an efficient lookup index split by model prefix for faster lookups.
This allows loading only the relevant chunk instead of the entire 27MB index.
"""
import gzip
import json
from collections import defaultdict

def create_lookup_index():
    """Create lookup index split by model prefix (first part before /)"""
    print("Loading component index...")
    with gzip.open('components/component_index.json.gz', 'rt') as f:
        index_data = json.load(f)
    
    component_index = index_data['component_index']
    
    # Group by prefix (e.g., "zera09" for "zera09/SmolVLM")
    lookup_chunks = defaultdict(dict)
    
    for model_id, component_id in component_index.items():
        # Get prefix (part before first /)
        if '/' in model_id:
            prefix = model_id.split('/')[0]
        else:
            prefix = '_other'  # Models without /
        
        lookup_chunks[prefix][model_id] = component_id
    
    # Save each chunk
    total_size = 0
    for prefix, chunk in lookup_chunks.items():
        chunk_file = f'components/lookup_{prefix}.json.gz'
        with gzip.open(chunk_file, 'wt', encoding='utf-8') as f:
            json.dump(chunk, f)
        
        file_size = __import__('os').path.getsize(chunk_file) / (1024 * 1024)
        total_size += file_size
        print(f"  {prefix}: {len(chunk):,} models, {file_size:.2f} MB")
    
    # Create index of prefixes
    prefix_index = {
        'prefixes': list(lookup_chunks.keys()),
        'total_models': len(component_index)
    }
    
    prefix_index_file = 'components/lookup_index.json.gz'
    with gzip.open(prefix_index_file, 'wt', encoding='utf-8') as f:
        json.dump(prefix_index, f)
    
    print(f"\n✓ Lookup index created:")
    print(f"  Prefixes: {len(lookup_chunks)}")
    print(f"  Total size: {total_size:.2f} MB")
    print(f"  Prefix index: {prefix_index_file}")
    
    return prefix_index_file

if __name__ == '__main__':
    create_lookup_index()

