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
    const searchParams = url.searchParams;
    
    // Use Worker's Cache API for component index (persists across requests)
    async function getComponentIndex(cache) {
      // Try cache first
      const cacheKey = 'https://cache/component_index';
      const cached = await cache.match(cacheKey);
      if (cached) {
        const cachedData = await cached.json();
        return cachedData.index;
      }
      
      // Load from R2 (try compact lookup first, fallback to full index)
      let indexObject = await env.AI_ECOSYSTEM_GRAPH.get('components/model_lookup.json.gz');
      if (!indexObject) {
        indexObject = await env.AI_ECOSYSTEM_GRAPH.get('components/component_index.json.gz');
        if (!indexObject) {
          throw new Error('Component index not found');
        }
      }
      
      // Decompress and parse index
      const compressedData = await indexObject.arrayBuffer();
      const stream = new DecompressionStream('gzip');
      const decompressedStream = new Response(compressedData).body.pipeThrough(stream);
      const decompressedData = await new Response(decompressedStream).arrayBuffer();
      const jsonText = new TextDecoder().decode(decompressedData);
      const indexData = JSON.parse(jsonText);
      
      // Extract index (handle both formats)
      const index = indexData.index || indexData.component_index;
      
      // Cache for 1 hour
      const cacheResponse = new Response(JSON.stringify({ index }), {
        headers: { 'Cache-Control': 'public, max-age=3600' }
      });
      await cache.put(cacheKey, cacheResponse);
      
      return index;
    }
    
    // Handle search API: /search?q=query (returns matching model IDs)
    if (pathname === '/search') {
      const query = searchParams.get('q') || '';
      const limit = parseInt(searchParams.get('limit') || '10');
      
      if (query.length < 2) {
        return new Response(JSON.stringify({ matches: [] }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
      
      try {
        const cache = caches.default;
        const index = await getComponentIndex(cache);
        const queryLower = query.toLowerCase();
        
        // Search through model IDs
        const matches = [];
        for (const modelId of Object.keys(index)) {
          if (modelId.toLowerCase().includes(queryLower)) {
            matches.push({
              id: modelId,
              name: modelId.split('/').pop()
            });
            if (matches.length >= limit) break;
          }
        }
        
        return new Response(JSON.stringify({ matches }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=300',
          },
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message, matches: [] }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
    }
    
    // Handle lookup API: /lookup?model_id=xxx (returns component_id)
    if (pathname === '/lookup') {
      const modelId = searchParams.get('model_id');
      if (!modelId) {
        return new Response(JSON.stringify({ error: 'model_id parameter required' }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
      
      try {
        const cache = caches.default;
        const index = await getComponentIndex(cache);
        const componentId = index[modelId];
        
        if (componentId === undefined) {
          return new Response(JSON.stringify({ error: 'Model not found', component_id: null }), {
            status: 404,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            },
          });
        }
        
        return new Response(JSON.stringify({ component_id: componentId }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=3600',
          },
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
    }
    
    // Determine which file to serve
    let r2Key;
    
    if (pathname === '/compact_index.json.gz' || pathname.includes('compact_index')) {
      // Serve compact index (array format, most efficient)
      r2Key = 'components/compact_index.json.gz';
    } else if (pathname === '/model_lookup.json.gz' || pathname.includes('model_lookup')) {
      // Serve compact model lookup file
      r2Key = 'components/model_lookup.json.gz';
    } else if (pathname === '/search_index.json.gz' || pathname.includes('search_index')) {
      // Serve search index (lightweight, just model IDs)
      r2Key = 'components/search_index.json.gz';
    } else if (pathname === '/' || pathname === '/component_index.json.gz' || pathname.includes('component_index')) {
      // Serve component index (full mapping - fallback)
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

