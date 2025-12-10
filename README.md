# AI Ecosystem Dashboard

A 3D interactive visualization of the AI model ecosystem network, built with Three.js. Explore relationships between AI models, their dependencies, and connections in an immersive 3D environment.

## Features

- **3D Network Visualization**: Interactive 3D force-directed graph showing model relationships
- **Dynamic Component Loading**: Search for any model and visualize its connected component
- **Edge Type Filtering**: Filter by relationship types (finetune, quantized, adapter, etc.)
- **Model Search**: Autocomplete search to quickly find models
- **Interactive Controls**: Zoom, pan, rotate, and click on nodes for details

## Project Structure

```
.
├── index.html              # Main front-end application
├── visualization_3d.html   # Original visualization (legacy)
├── graph_data.json         # Full dataset (500MB - excluded from git)
├── graph_data_mini.json    # Mini sample for testing (~700KB)
├── front-end-visualization.ipynb  # Jupyter notebook for data processing
├── create_mini_sample.py   # Script to generate mini samples
├── requirements.txt        # Python dependencies
└── data/                   # Source data directory
    └── ai_ecosystem_graph_nomerges.pkl
```

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bendlaufer/ai-ecosystem-dashboard.git
   cd ai-ecosystem-dashboard
   ```

2. **Set up Python environment** (for data processing)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Generate mini sample** (optional, for testing)
   ```bash
   python create_mini_sample.py
   ```

4. **Run local server**
   ```bash
   # Option 1: Python
   python -m http.server 8000
   
   # Option 2: Node.js
   npx http-server -p 8000
   
   # Then open: http://localhost:8000
   ```

### Using the Visualization

1. **Start with Mini Sample**: The default data source is `graph_data_mini.json` (for testing)
2. **Switch to Full Dataset**: Use the dropdown to select `graph_data.json` (requires the full 500MB file)
3. **Search for Models**: Type a model ID in the search box (e.g., `meta-llama/Llama-3-8B`)
4. **Explore**: Click on nodes to see details, use mouse to rotate/zoom/pan

## Data Files

- **graph_data_mini.json**: Small sample (~50 nodes) for quick testing
- **graph_data.json**: Full dataset (1.8M+ nodes, 500MB) - must be generated locally

### Generating the Full Dataset

Run the Jupyter notebook `front-end-visualization.ipynb` to generate `graph_data.json` from the source pickle file.

## Deployment

### GitHub Pages

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Select source branch (usually `main`)
   - Select folder: `/ (root)`
   - Click Save

2. **Access your site**: `https://bendlaufer.github.io/ai-ecosystem-dashboard/`

### Other Hosting Options

- **Netlify**: Drag and drop the folder or connect your GitHub repo
- **Vercel**: Connect GitHub repo for automatic deployments
- **Any static hosting**: Upload `index.html` and data files

## Notes

- The full `graph_data.json` (500MB) is excluded from git via `.gitignore`
- For production, consider hosting the large data file on a CDN or using lazy loading
- The mini sample is included for demonstration purposes

## Technologies

- **Three.js**: 3D graphics and visualization
- **NetworkX**: Graph processing (Python)
- **Pandas**: Data manipulation (Python)

## License

MIT License - feel free to use and modify!

