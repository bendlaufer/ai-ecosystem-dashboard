"""
Create chunked lookup index files organized alphabetically.
Each chunk contains models starting with the same first 2 characters.
"""
import gzip
import json
import os
from collections import defaultdict

def create_chunked_index():
    """Split component index into chunks by first 2 characters of model ID"""
    print("Loading component index...")
    
    # Load the full component index
    with gzip.open('components/component_index.json.gz', 'rt') as f:
        index_data = json.load(f)
    
    component_index = index_data['component_index']
    print(f"Total models: {len(component_index):,}")
    
    # Group by first 2 characters (case-insensitive, alphanumeric)
    chunks = defaultdict(dict)
    
    for modelId, componentId in component_index.items():
        # Get first 2 characters, convert to lowercase
        # Handle edge cases (single char, empty, special chars)
        prefix = modelId[:2].lower() if len(modelId) >= 2 else modelId[0].lower() if len(modelId) == 1 else '00'
        
        # Normalize: only alphanumeric, fallback to '00' for special chars
        if not prefix[0].isalnum():
            prefix = '00'
        elif len(prefix) == 1:
            prefix = prefix + '0'
        
        chunks[prefix][modelId] = componentId
    
    # Create chunks directory
    os.makedirs('components/chunks', exist_ok=True)
    
    # Save each chunk
    chunk_files = []
    total_chunks = len(chunks)
    
    for prefix, chunk_data in sorted(chunks.items()):
        chunk_file = f'components/chunks/lookup_{prefix}.json.gz'
        
        chunk_info = {
            'prefix': prefix,
            'index': chunk_data,
            'count': len(chunk_data)
        }
        
        with gzip.open(chunk_file, 'wt', encoding='utf-8') as f:
            json.dump(chunk_info, f)
        
        file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
        chunk_files.append({
            'prefix': prefix,
            'file': chunk_file,
            'count': len(chunk_data),
            'size_mb': file_size_mb
        })
        
        print(f"  {prefix}: {len(chunk_data):,} models, {file_size_mb:.2f} MB")
    
    # Create index of chunks (metadata file)
    chunks_index = {
        'chunks': {c['prefix']: {'file': c['file'], 'count': c['count'], 'size_mb': c['size_mb']} 
                   for c in chunk_files},
        'total_chunks': total_chunks,
        'total_models': len(component_index)
    }
    
    with gzip.open('components/chunks_index.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(chunks_index, f)
    
    print(f"\n✓ Created {total_chunks} chunk files")
    print(f"✓ Chunks index: components/chunks_index.json.gz")
    
    # Show statistics
    sizes = [c['size_mb'] for c in chunk_files]
    print(f"\nChunk size stats:")
    print(f"  Min: {min(sizes):.2f} MB")
    print(f"  Max: {max(sizes):.2f} MB")
    print(f"  Avg: {sum(sizes)/len(sizes):.2f} MB")
    
    return chunk_files

if __name__ == '__main__':
    create_chunked_index()

