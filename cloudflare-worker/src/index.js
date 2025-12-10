export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // Determine which file to serve
    let r2Key;
    
    if (pathname === '/' || pathname === '/component_index.json.gz' || pathname.includes('component_index')) {
      // Serve component index
      r2Key = 'components/component_index.json.gz';
    } else if (pathname.match(/\/component_\d+\.json\.gz$/)) {
      // Serve specific component (e.g., /component_0.json.gz)
      const filename = pathname.split('/').pop();
      r2Key = `components/${filename}`;
    } else {
      // Fallback: serve full graph (legacy support)
      r2Key = 'graph_data.json.gz';
    }

    // Fetch from R2 bucket
    const object = await env.AI_ECOSYSTEM_GRAPH.get(r2Key);
    
    if (!object) {
      return new Response(`File not found: ${r2Key}`, { status: 404 });
    }

    // Stream the gzipped file directly (don't decompress - let browser handle it)
    const body = object.body;
    const size = object.size;

    // Build headers
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
      'Content-Type': 'application/gzip',
      'Cache-Control': 'public, max-age=3600',
    };
    
    // Add Content-Length if available
    if (size) {
      headers['Content-Length'] = size.toString();
    }

    // Return gzipped file with CORS headers
    // Browser will decompress using DecompressionStream API
    return new Response(body, { headers });
  },
};

