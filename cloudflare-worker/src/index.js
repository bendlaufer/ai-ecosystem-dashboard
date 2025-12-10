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

    // Get the compressed data
    const compressedData = await object.arrayBuffer();
    
    // Decompress using the built-in DecompressionStream
    const stream = new DecompressionStream('gzip');
    const decompressedStream = new Response(compressedData).body.pipeThrough(stream);
    const decompressedData = await new Response(decompressedStream).arrayBuffer();

    // Return decompressed JSON with CORS headers
    return new Response(decompressedData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=3600',
      },
    });
  },
};

