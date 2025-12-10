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

    const data = await object.arrayBuffer();

    // Return with CORS headers
    return new Response(data, {
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

