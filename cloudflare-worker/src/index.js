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

    // Fetch from R2 bucket
    const object = await env.AI_ECOSYSTEM_GRAPH.get('graph_data.json.gz');
    
    if (!object) {
      return new Response('File not found', { status: 404 });
    }

    // Stream the gzipped file directly (don't decompress - let browser handle it)
    // This avoids Worker timeout/memory issues with large files
    const body = object.body;

    // Return gzipped file with CORS headers
    // Browser will decompress using DecompressionStream API
    return new Response(body, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
        'Content-Type': 'application/gzip',
        'Content-Encoding': 'gzip',
        'Cache-Control': 'public, max-age=3600',
      },
    });
  },
};

