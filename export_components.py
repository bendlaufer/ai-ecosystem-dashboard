"""
Export graph data as separate connected components with an index.
This allows loading only the needed component instead of the entire 570MB file.
"""
import pickle
import networkx as nx
import json
import gzip
from collections import defaultdict
import os

def export_components(G, output_dir='components', include_attributes=['likes', 'downloads', 'createdAt', 'pipeline_tag', 'library_name']):
    """
    Export graph as separate connected components with an index.
    
    Parameters:
    - G: networkx graph
    - output_dir: directory to save component files
    - include_attributes: list of node attributes to include
    """
    print(f"Processing graph: {len(G.nodes())} nodes, {len(G.edges())} edges")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all connected components
    print("Finding connected components...")
    components = list(nx.connected_components(G))
    print(f"Found {len(components)} connected components")
    
    # Create index: model_id -> component_id
    component_index = {}
    component_stats = []
    
    # Process each component
    for comp_id, component_nodes in enumerate(components):
        comp_size = len(component_nodes)
        print(f"Processing component {comp_id}: {comp_size} nodes")
        
        # Map all nodes in this component to component_id
        for node_id in component_nodes:
            component_index[node_id] = comp_id
        
        # Build subgraph for this component
        G_sub = G.subgraph(component_nodes).copy()
        
        # Prepare nodes data
        nodes_data = []
        for node_id in G_sub.nodes():
            node_data = {
                'id': node_id,
                'name': node_id.split('/')[-1] if '/' in node_id else node_id
            }
            
            # Add requested attributes
            for attr in include_attributes:
                if attr in G_sub.nodes[node_id]:
                    value = G_sub.nodes[node_id][attr]
                    if hasattr(value, '__iter__') and not isinstance(value, str):
                        # Skip non-serializable types
                        continue
                    try:
                        import pandas as pd
                        if hasattr(pd, 'isna') and pd.isna(value):
                            node_data[attr] = None
                        elif value != value:  # Check for NaN
                            node_data[attr] = None
                        else:
                            node_data[attr] = value
                    except:
                        node_data[attr] = None
            
            node_data['size'] = 1.0
            node_data['downloads'] = G_sub.nodes[node_id].get('downloads', 0)
            node_data['likes'] = G_sub.nodes[node_id].get('likes', 0)
            nodes_data.append(node_data)
        
        # Prepare edges data
        edges_data = []
        for source, target in G_sub.edges():
            edge_data = {
                'source': source,
                'target': target
            }
            
            # Add edge attributes
            if 'edge_type' in G_sub.edges[source, target]:
                edge_data['type'] = G_sub.edges[source, target]['edge_type']
            elif 'edge_types' in G_sub.edges[source, target]:
                edge_types = G_sub.edges[source, target]['edge_types']
                edge_data['type'] = edge_types[0] if edge_types else 'unknown'
            else:
                edge_data['type'] = 'unknown'
            
            edges_data.append(edge_data)
        
        # Create component JSON
        component_json = {
            'nodes': nodes_data,
            'edges': edges_data,
            'metadata': {
                'component_id': comp_id,
                'total_nodes': len(nodes_data),
                'total_edges': len(edges_data)
            }
        }
        
        # Save component (compressed)
        component_file = os.path.join(output_dir, f'component_{comp_id}.json.gz')
        with gzip.open(component_file, 'wt', encoding='utf-8') as f:
            json.dump(component_json, f)
        
        # Track stats
        file_size_mb = os.path.getsize(component_file) / (1024 * 1024)
        component_stats.append({
            'component_id': comp_id,
            'nodes': comp_size,
            'edges': len(edges_data),
            'file_size_mb': round(file_size_mb, 2),
            'sample_models': list(component_nodes)[:5]  # First 5 models as examples
        })
        
        print(f"  Saved: {component_file} ({file_size_mb:.2f} MB)")
    
    # Create index file
    index_data = {
        'component_index': component_index,
        'component_stats': component_stats,
        'total_components': len(components),
        'total_nodes': len(G.nodes()),
        'total_edges': len(G.edges())
    }
    
    # Save index (compressed)
    index_file = os.path.join(output_dir, 'component_index.json.gz')
    with gzip.open(index_file, 'wt', encoding='utf-8') as f:
        json.dump(index_data, f)
    
    index_size_mb = os.path.getsize(index_file) / (1024 * 1024)
    print(f"\n✓ Index saved: {index_file} ({index_size_mb:.2f} MB)")
    print(f"✓ Total components: {len(components)}")
    print(f"✓ Total files: {len(components)} components + 1 index")
    
    # Print summary
    print("\nComponent size distribution:")
    size_buckets = defaultdict(int)
    for stat in component_stats:
        if stat['nodes'] < 10:
            size_buckets['< 10'] += 1
        elif stat['nodes'] < 100:
            size_buckets['10-100'] += 1
        elif stat['nodes'] < 1000:
            size_buckets['100-1K'] += 1
        elif stat['nodes'] < 10000:
            size_buckets['1K-10K'] += 1
        else:
            size_buckets['> 10K'] += 1
    
    for bucket, count in sorted(size_buckets.items()):
        print(f"  {bucket} nodes: {count} components")
    
    return index_file, component_stats

if __name__ == '__main__':
    import pandas as pd
    
    # Load graph
    print("Loading graph...")
    with open('data/ai_ecosystem_graph_nomerges.pkl', 'rb') as f:
        G = pickle.load(f)
    
    print(f"Graph loaded: {len(G.nodes())} nodes, {len(G.edges())} edges\n")
    
    # Export components
    index_file, stats = export_components(
        G,
        output_dir='components',
        include_attributes=['likes', 'downloads', 'createdAt', 'pipeline_tag', 'library_name']
    )
    
    print(f"\n✓ Export complete!")
    print(f"  Index file: {index_file}")
    print(f"  Components directory: components/")
    print(f"\nNext steps:")
    print(f"  1. Upload components/ directory to R2 bucket")
    print(f"  2. Update frontend to load index first, then load components on demand")

