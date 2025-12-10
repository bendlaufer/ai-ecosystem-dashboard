"""
Create a more memory-efficient index format.
Instead of a plain object, use an array of tuples for better memory efficiency.
"""
import gzip
import json

def create_compact_index():
    """Create compact index as array of [modelId, componentId] tuples"""
    print("Loading component index...")
    with gzip.open('components/component_index.json.gz', 'rt') as f:
        index_data = json.load(f)
    
    component_index = index_data['component_index']
    
    # Convert to array of tuples (more memory efficient than object)
    # Format: [[modelId1, componentId1], [modelId2, componentId2], ...]
    index_array = [[modelId, componentId] for modelId, componentId in component_index.items()]
    
    # Sort by modelId for binary search capability
    index_array.sort(key=lambda x: x[0])
    
    compact_index = {
        'index': index_array,
        'total_models': len(index_array)
    }
    
    # Save compact index
    compact_file = 'components/compact_index.json.gz'
    with gzip.open(compact_file, 'wt', encoding='utf-8') as f:
        json.dump(compact_index, f)
    
    file_size_mb = __import__('os').path.getsize(compact_file) / (1024 * 1024)
    print(f"✓ Compact index created: {compact_file}")
    print(f"  Models: {len(index_array):,}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Format: Array of [modelId, componentId] tuples (sorted)")
    
    return compact_file

if __name__ == '__main__':
    create_compact_index()

