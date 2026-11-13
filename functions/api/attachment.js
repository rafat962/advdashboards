/**
 * Cloudflare Pages Function: /api/attachment
 * Serves files from R2 securely — Canvas/viewer only, blocks direct browser access and download tools.
 *
 * Required:
 *   - R2 bucket binding "MY_BUCKET" in Cloudflare Pages settings
 *   - Query param: ?key=<R2_File_Key>
 *   - Request header: X-Viewer-Mode: canvas-render  (sent by the frontend viewer only)
 *
 * Security checks:
 *   1. Rejects direct browser navigation (Sec-Fetch-Dest: document)
 *   2. Rejects any request missing the X-Viewer-Mode: canvas-render header
 *   3. Returns binary stream with headers that prevent caching and sniffing
 *   4. Returns X-User-Identity header for watermark rendering in the frontend canvas
 */
export async function onRequest(context) {
  const { request, env } = context;

  // --- Security gate 1: Block direct browser navigation ---
  const fetchDest = request.headers.get('Sec-Fetch-Dest');
  if (fetchDest === 'document') {
    return new Response('403 Forbidden — Direct access not allowed', {
      status: 403,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // --- Security gate 2: Require custom viewer header ---
  const viewerMode = request.headers.get('X-Viewer-Mode');
  if (viewerMode !== 'canvas-render') {
    return new Response('403 Forbidden — Use the in-app viewer to access this file', {
      status: 403,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // --- Read R2 key from query string ---
  const url = new URL(request.url);
  const key = url.searchParams.get('key');

  if (!key || key.trim() === '') {
    return new Response('400 Bad Request — Missing file key', {
      status: 400,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // --- Validate key: prevent path traversal ---
  if (key.includes('..') || key.startsWith('/')) {
    return new Response('400 Bad Request — Invalid key', {
      status: 400,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // --- R2 bucket access ---
  if (!env.MY_BUCKET) {
    return new Response('503 Service Unavailable — R2 bucket not configured', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  const object = await env.MY_BUCKET.get(key);

  if (!object) {
    return new Response('404 Not Found — File does not exist', {
      status: 404,
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // --- User identity for watermark (from Cloudflare Access header or fallback) ---
  const userIdentity =
    request.headers.get('Cf-Access-Authenticated-User-Email') || 'Authorized-Viewer';

  // --- Return binary stream with security headers ---
  return new Response(object.body, {
    status: 200,
    headers: {
      'Content-Type': 'application/octet-stream',
      'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      'Pragma': 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Content-Disposition': 'inline',
      'X-User-Identity': userIdentity,
    },
  });
}

