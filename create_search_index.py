"""
Create a lightweight search index (just model IDs) for autocomplete.
The full component mapping will be loaded on-demand when needed.
"""
import gzip
import json

def create_search_index():
    """Create a lightweight search index with just model IDs"""
    print("Loading component index...")
    with gzip.open('components/component_index.json.gz', 'rt') as f:
        index_data = json.load(f)
    
    component_index = index_data['component_index']
    
    # Create search index: just sorted model IDs
    model_ids = sorted(component_index.keys())
    
    search_index = {
        'model_ids': model_ids,
        'total_models': len(model_ids)
    }
    
    # Save search index (compressed)
    search_index_file = 'components/search_index.json.gz'
    with gzip.open(search_index_file, 'wt', encoding='utf-8') as f:
        json.dump(search_index, f)
    
    file_size_mb = __import__('os').path.getsize(search_index_file) / (1024 * 1024)
    print(f"✓ Search index created: {search_index_file}")
    print(f"  Models: {len(model_ids):,}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  (Much smaller than full index: ~27MB)")
    
    return search_index_file

if __name__ == '__main__':
    create_search_index()

