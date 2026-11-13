/**
 * Cloudflare Pages Function: /api/esri-token
 * Generates an Esri OAuth2 client_credentials token server-side.
 * Required env vars (set in Cloudflare Pages dashboard → Settings → Environment Variables):
 *   ESRI_CLIENT_ID, ESRI_CLIENT_SECRET, ESRI_PORTAL_URL (optional, defaults to https://www.arcgis.com)
 */
export async function onRequest(context) {
  const { ESRI_CLIENT_ID, ESRI_CLIENT_SECRET, ESRI_PORTAL_URL } = context.env;

  if (!ESRI_CLIENT_ID || !ESRI_CLIENT_SECRET) {
    return new Response(
      JSON.stringify({ error: 'Missing ESRI credentials in environment variables' }),
      { status: 500, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } }
    );
  }

  const portalUrl = (ESRI_PORTAL_URL || 'https://www.arcgis.com').replace(/\/$/, '');

  const body = new URLSearchParams({
    client_id: ESRI_CLIENT_ID,
    client_secret: ESRI_CLIENT_SECRET,
    grant_type: 'client_credentials',
    expiration: '60',
    f: 'json',
  });

  try {
    const resp = await fetch(`${portalUrl}/sharing/rest/oauth2/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    });

    const data = await resp.json();

    if (data.error) {
      return new Response(
        JSON.stringify({ error: data.error.message || 'Esri token error', details: data.error }),
        { status: 502, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } }
      );
    }

    return new Response(
      JSON.stringify({ access_token: data.access_token, expires_in: data.expires_in }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-store',
        },
      }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: 'Failed to reach Esri portal', message: err.message }),
      { status: 503, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } }
    );
  }
}

