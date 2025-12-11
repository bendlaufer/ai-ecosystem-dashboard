#!/usr/bin/env python3
"""
Create a magazine cover visualization of 40 randomly selected model families
in 3D force layout, formatted for 8.5x11 inch print.
"""

import json
import gzip
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Rectangle
import os

# Configuration
DPI = 300  # Print quality
WIDTH_INCHES = 8.5
HEIGHT_INCHES = 11
COMPONENTS_DIR = "components"  # Directory containing component JSON files
OUTPUT_FILE = "magazine_cover_visualization.png"
NUM_COMPONENTS = 40
MIN_NODES = 3
MAX_NODES = 1200

# Prefer components 1-500 (70% chance)
def get_random_component_id():
    if random.random() < 0.7:
        return random.randint(1, 500)
    else:
        return random.randint(501, 10000)

# Load a component from file
def load_component(component_id):
    """Load a component JSON file."""
    file_path = os.path.join(COMPONENTS_DIR, f"component_{component_id}.json.gz")
    if not os.path.exists(file_path):
        return None
    
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading component {component_id}: {e}")
        return None

# Simple 3D force-directed layout
def compute_3d_layout(graph, iterations=100):
    """Compute 3D force-directed layout for a graph."""
    n = len(graph.nodes())
    if n == 0:
        return {}
    
    # Initialize positions randomly
    pos = {node: np.random.rand(3) * 10 - 5 for node in graph.nodes()}
    
    # Force parameters (conservative for stability)
    repulsion = 0.1 / np.sqrt(n / 100) if n > 1200 else 0.1
    attraction = 0.01 if n <= 1200 else 0.002
    damping = 0.9 if n <= 1200 else 0.8
    
    for _ in range(iterations):
        # Calculate forces
        forces = {node: np.zeros(3) for node in graph.nodes()}
        
        # Repulsion between all nodes
        nodes_list = list(graph.nodes())
        for i, node1 in enumerate(nodes_list):
            for node2 in nodes_list[i+1:]:
                vec = pos[node1] - pos[node2]
                dist = np.linalg.norm(vec)
                if dist > 0:
                    force = repulsion / (dist * dist + 1)
                    direction = vec / dist
                    forces[node1] += direction * force
                    forces[node2] -= direction * force
        
        # Attraction along edges
        for edge in graph.edges():
            node1, node2 = edge
            vec = pos[node2] - pos[node1]
            dist = np.linalg.norm(vec)
            if dist > 0:
                k = np.sqrt(n * 100 / n)
                force = (dist - k) * attraction
                direction = vec / dist
                forces[node1] += direction * force
                forces[node2] -= direction * force
        
        # Update positions
        for node in graph.nodes():
            pos[node] += forces[node] * 0.1
            pos[node] *= damping
    
    return pos

# Create visualization for a single component
def visualize_component_3d(ax, component_data, x_offset=0, y_offset=0, z_offset=0, scale=1.0):
    """Visualize a single component in 3D on the given axes."""
    # Create graph from component data
    G = nx.DiGraph()
    
    # Add nodes
    for node in component_data['nodes']:
        G.add_node(node['id'], **node)
    
    # Add edges
    for edge in component_data['edges']:
        G.add_edge(edge['source'], edge['target'], **edge)
    
    if len(G.nodes()) == 0:
        return
    
    # Compute layout
    pos = compute_3d_layout(G, iterations=50)
    
    # Edge colors
    edge_colors = {
        'finetune': '#ff6b6b',
        'quantized': '#4ecdc4',
        'adapter': '#45b7d1',
        'unknown': '#96ceb4',
        'default': '#cccccc'
    }
    
    # Draw edges
    for edge in component_data['edges']:
        source = edge['source']
        target = edge['target']
        if source in pos and target in pos:
            edge_type = edge.get('type', 'unknown')
            color = edge_colors.get(edge_type, edge_colors['default'])
            
            x = [pos[source][0] * scale + x_offset, pos[target][0] * scale + x_offset]
            y = [pos[source][1] * scale + y_offset, pos[target][1] * scale + y_offset]
            z = [pos[source][2] * scale + z_offset, pos[target][2] * scale + z_offset]
            
            ax.plot(x, y, z, color=color, alpha=0.3, linewidth=0.5)
    
    # Draw nodes
    # Determine which nodes have children (parents)
    has_children = set()
    for edge in component_data['edges']:
        has_children.add(edge['source'])
    
    xs, ys, zs = [], [], []
    colors = []
    sizes = []
    
    for node in component_data['nodes']:
        node_id = node['id']
        if node_id in pos:
            xs.append(pos[node_id][0] * scale + x_offset)
            ys.append(pos[node_id][1] * scale + y_offset)
            zs.append(pos[node_id][2] * scale + z_offset)
            
            # Color: red for parents, cyan for leaves
            if node_id in has_children:
                colors.append('#ff6b6b')
                sizes.append(20)
            else:
                colors.append('#4ecdc4')
                sizes.append(10)
    
    ax.scatter(xs, ys, zs, c=colors, s=sizes, alpha=0.8, edgecolors='white', linewidths=0.5)

def main():
    print("Creating magazine cover visualization...")
    print(f"Target: {NUM_COMPONENTS} components, {WIDTH_INCHES}x{HEIGHT_INCHES} inches at {DPI} DPI")
    
    # Check if components directory exists
    if not os.path.exists(COMPONENTS_DIR):
        print(f"Error: Components directory '{COMPONENTS_DIR}' not found!")
        print("Please ensure component files are in the components/ directory.")
        return
    
    # Collect valid components
    print("\nCollecting valid components...")
    valid_components = []
    attempts = 0
    max_attempts = 500
    
    while len(valid_components) < NUM_COMPONENTS and attempts < max_attempts:
        component_id = get_random_component_id()
        component_data = load_component(component_id)
        
        if component_data and 'nodes' in component_data:
            node_count = len(component_data['nodes'])
            if MIN_NODES <= node_count <= MAX_NODES:
                valid_components.append((component_id, component_data))
                print(f"  Found component {component_id}: {node_count} nodes")
        
        attempts += 1
        
        # Try next component if current one is invalid
        if component_data is None or (component_data and 'nodes' in component_data and 
                                     not (MIN_NODES <= len(component_data['nodes']) <= MAX_NODES)):
            component_id += 1
            if component_id > 10000:
                component_id = 1
    
    if len(valid_components) < NUM_COMPONENTS:
        print(f"\nWarning: Only found {len(valid_components)} valid components out of {NUM_COMPONENTS} requested.")
        print("Proceeding with available components...")
    
    # Arrange components in a grid
    # 8 columns, 5 rows for 40 components
    cols = 8
    rows = (len(valid_components) + cols - 1) // cols
    
    # Calculate spacing
    # Leave margins and space between components
    margin = 0.5  # inches
    spacing_x = 0.3  # inches between components
    spacing_y = 0.3
    
    usable_width = WIDTH_INCHES - 2 * margin
    usable_height = HEIGHT_INCHES - 2 * margin
    
    component_width = (usable_width - (cols - 1) * spacing_x) / cols
    component_height = (usable_height - (rows - 1) * spacing_y) / rows
    
    # Create figure
    fig = plt.figure(figsize=(WIDTH_INCHES, HEIGHT_INCHES), dpi=DPI)
    ax = fig.add_subplot(111, projection='3d')
    
    # Set background
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('white')
    ax.yaxis.pane.set_edgecolor('white')
    ax.zaxis.pane.set_edgecolor('white')
    ax.grid(False)
    ax.set_facecolor('white')
    
    # Visualize each component
    print(f"\nVisualizing {len(valid_components)} components...")
    for idx, (component_id, component_data) in enumerate(valid_components):
        row = idx // cols
        col = idx % cols
        
        # Calculate position
        x_offset = margin + col * (component_width + spacing_x) + component_width / 2
        y_offset = margin + (rows - 1 - row) * (component_height + spacing_y) + component_height / 2
        z_offset = 0
        
        # Scale to fit within component area
        scale = min(component_width, component_height) / 15.0
        
        print(f"  Component {component_id} at position ({row}, {col})")
        visualize_component_3d(ax, component_data, x_offset, y_offset, z_offset, scale)
    
    # Set axis limits to match page dimensions
    ax.set_xlim(0, WIDTH_INCHES)
    ax.set_ylim(0, HEIGHT_INCHES)
    ax.set_zlim(-2, 2)
    
    # Remove axis labels and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    
    # Adjust viewing angle for best visualization
    ax.view_init(elev=20, azim=45)
    
    # Save figure
    print(f"\nSaving to {OUTPUT_FILE}...")
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Saved: {OUTPUT_FILE}")
    print(f"  Dimensions: {WIDTH_INCHES}x{HEIGHT_INCHES} inches at {DPI} DPI")
    print(f"  Pixel dimensions: {int(WIDTH_INCHES * DPI)}x{int(HEIGHT_INCHES * DPI)}")
    
    plt.close()

if __name__ == "__main__":
    main()

