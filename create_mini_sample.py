"""
Script to create a mini sample of graph_data.json for testing the front-end.
This creates a small connected component with a few nodes and edges.
"""
import json
import random

def create_mini_sample(input_file='graph_data.json', output_file='graph_data_mini.json', max_nodes=None):
    """
    Create a mini sample from the full graph_data.json.
    Takes a random connected component or creates a small sample.
    """
    try:
        print(f"Loading {input_file}...")
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        print(f"Original: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
        
        # Strategy: Find a node with connections and build a small connected component
        if len(data['nodes']) == 0:
            raise ValueError("No nodes in input file!")
        
        # Create node and edge maps for efficient lookup
        node_map = {node['id']: node for node in data['nodes']}
        edges_by_source = {}
        edges_by_target = {}
        
        for edge in data['edges']:
            source = edge['source']
            target = edge['target']
            
            if source not in edges_by_source:
                edges_by_source[source] = []
            edges_by_source[source].append(edge)
            
            if target not in edges_by_target:
                edges_by_target[target] = []
            edges_by_target[target].append(edge)
        
        # Find a node that has connections
        nodes_with_edges = set()
        for edge in data['edges']:
            nodes_with_edges.add(edge['source'])
            nodes_with_edges.add(edge['target'])
        
        if not nodes_with_edges:
            raise ValueError("No edges found in graph!")
        
        # Start with the specific model: zera09/SmolVLM
        target_model = 'zera09/SmolVLM'
        if target_model not in node_map:
            print(f"Warning: {target_model} not found in graph. Using random node instead.")
            start_node_id = random.choice(list(nodes_with_edges))
        else:
            start_node_id = target_model
        print(f"Starting from node: {start_node_id}")
        
        # BFS to collect a small connected component
        visited = set()
        queue = [start_node_id]
        selected_nodes = set()
        selected_edges_dict = {}  # Use dict to store edges by (source, target) key
        
        while queue and (max_nodes is None or len(selected_nodes) < max_nodes):
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            if current in node_map:
                selected_nodes.add(current)
            
            # Add outgoing edges
            if current in edges_by_source:
                for edge in edges_by_source[current]:
                    target = edge['target']
                    if target in node_map:  # Make sure target exists
                        edge_key = (edge['source'], edge['target'])
                        selected_edges_dict[edge_key] = edge
                        if target not in visited and (max_nodes is None or len(selected_nodes) < max_nodes):
                            queue.append(target)
            
            # Add incoming edges
            if current in edges_by_target:
                for edge in edges_by_target[current]:
                    source = edge['source']
                    if source in node_map:  # Make sure source exists
                        edge_key = (edge['source'], edge['target'])
                        selected_edges_dict[edge_key] = edge
                        if source not in visited and (max_nodes is None or len(selected_nodes) < max_nodes):
                            queue.append(source)
        
        # Build the mini graph
        mini_nodes = [node_map[node_id] for node_id in selected_nodes if node_id in node_map]
        mini_edges = list(selected_edges_dict.values())
        
        if len(mini_nodes) == 0:
            raise ValueError("Could not create connected component!")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        print("Creating a mock sample instead...")
        
        # Create a mock sample
        mini_nodes = [
            {
                'id': 'meta-llama/Llama-3-8B',
                'name': 'Llama-3-8B',
                'likes': 5000,
                'downloads': 1000000,
                'createdAt': '2024-01-01T00:00:00.000Z',
                'pipeline_tag': 'text-generation',
                'library_name': 'transformers',
                'size': 1.0
            },
            {
                'id': 'meta-llama/Llama-3-8B-Instruct',
                'name': 'Llama-3-8B-Instruct',
                'likes': 3000,
                'downloads': 800000,
                'createdAt': '2024-02-01T00:00:00.000Z',
                'pipeline_tag': 'text-generation',
                'library_name': 'transformers',
                'size': 1.0
            },
            {
                'id': 'user/finetuned-llama',
                'name': 'finetuned-llama',
                'likes': 100,
                'downloads': 5000,
                'createdAt': '2024-03-01T00:00:00.000Z',
                'pipeline_tag': 'text-generation',
                'library_name': 'transformers',
                'size': 1.0
            },
            {
                'id': 'user/quantized-llama',
                'name': 'quantized-llama',
                'likes': 50,
                'downloads': 2000,
                'createdAt': '2024-04-01T00:00:00.000Z',
                'pipeline_tag': 'text-generation',
                'library_name': 'transformers',
                'size': 1.0
            }
        ]
        mini_edges = [
            {
                'source': 'meta-llama/Llama-3-8B',
                'target': 'meta-llama/Llama-3-8B-Instruct',
                'type': 'finetune'
            },
            {
                'source': 'meta-llama/Llama-3-8B',
                'target': 'user/finetuned-llama',
                'type': 'finetune'
            },
            {
                'source': 'meta-llama/Llama-3-8B-Instruct',
                'target': 'user/quantized-llama',
                'type': 'quantized'
            }
        ]
    
    mini_data = {
        'nodes': mini_nodes,
        'edges': mini_edges,
        'metadata': {
            'total_nodes': len(mini_nodes),
            'total_edges': len(mini_edges),
            'full_graph': True,  # Mark as full graph so the UI works correctly
            'sample': True,
            'original_size': len(data.get('nodes', [])) if 'data' in locals() else 0
        }
    }
    
    print(f"Mini sample: {len(mini_nodes)} nodes, {len(mini_edges)} edges")
    print(f"Saving to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(mini_data, f, indent=2)
    
    file_size_kb = len(json.dumps(mini_data)) / 1024
    print(f"✓ Mini sample created successfully!")
    print(f"  File size: {file_size_kb:.2f} KB")
    
    return mini_data

if __name__ == '__main__':
    create_mini_sample()
