/**
 * Cloudflare Worker for AdvDashboards
 * Provides HMAC-SHA256 cookie-based authentication and route protection for static assets.
 */

// Helper to encode ArrayBuffer to Base64Url
function bufferToBase64Url(buf) {
    const bytes = new Uint8Array(buf);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

// Helper to decode Base64Url to Uint8Array
function base64UrlToBuffer(b64url) {
    let b64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
    while (b64.length % 4 !== 0) {
        b64 += "=";
    }
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}

// UTF-8 safe Base64Url encoding
function strToBase64Url(str) {
    const bytes = new TextEncoder().encode(str);
    return bufferToBase64Url(bytes);
}

// UTF-8 safe Base64Url decoding
function base64UrlToStr(b64url) {
    const bytes = base64UrlToBuffer(b64url);
    return new TextDecoder().decode(bytes);
}

// Derive CryptoKey for HMAC-SHA256 from secret
async function getCryptoKey(secret) {
    return await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(secret),
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign", "verify"]
    );
}

// Create signed token: payload.signature
async function createToken(username, maxAgeSec, secret) {
    const exp = Date.now() + maxAgeSec * 1000;
    const payloadJson = JSON.stringify({ u: username, exp });
    const b64Payload = strToBase64Url(payloadJson);
    const key = await getCryptoKey(secret);
    const sigBuffer = await crypto.subtle.sign(
        "HMAC",
        key,
        new TextEncoder().encode(b64Payload)
    );
    const b64Sig = bufferToBase64Url(sigBuffer);
    return `${b64Payload}.${b64Sig}`;
}

// Verify signed token
async function verifyToken(token, secret, users) {
    if (!token || typeof token !== "string") return null;
    const parts = token.split(".");
    if (parts.length !== 2) return null;
    const [b64Payload, b64Sig] = parts;

    try {
        const key = await getCryptoKey(secret);
        const sigBytes = base64UrlToBuffer(b64Sig);
        const dataBytes = new TextEncoder().encode(b64Payload);

        const isValid = await crypto.subtle.verify("HMAC", key, sigBytes, dataBytes);
        if (!isValid) return null;

        const payloadJson = base64UrlToStr(b64Payload);
        const payload = JSON.parse(payloadJson);

        if (!payload.u || !payload.exp) return null;
        if (Date.now() > payload.exp) return null;
        if (users && !Object.prototype.hasOwnProperty.call(users, payload.u)) return null;

        return payload.u;
    } catch (e) {
        return null;
    }
}

// Parse cookie value from request header
function getCookie(request, name) {
    const cookieHeader = request.headers.get("Cookie");
    if (!cookieHeader) return null;
    const cookies = cookieHeader.split(";");
    for (const c of cookies) {
        const [k, ...v] = c.trim().split("=");
        if (k === name) {
            return decodeURIComponent(v.join("="));
        }
    }
    return null;
}

export default {
    async fetch(request, env) {
        const rawUsers = env.AUTH_USERS;
        if (!rawUsers) {
            return new Response("Server Auth Configuration Missing: env.AUTH_USERS is not set", {
                status: 500,
                headers: { "Content-Type": "text/plain; charset=utf-8" },
            });
        }

        let USERS = {};
        let secretKeyStr = "";
        if (typeof rawUsers === "object" && rawUsers !== null) {
            USERS = rawUsers;
            secretKeyStr = JSON.stringify(rawUsers);
        } else if (typeof rawUsers === "string") {
            try {
                USERS = JSON.parse(rawUsers);
                secretKeyStr = rawUsers;
            } catch (e) {
                return new Response("Invalid AUTH_USERS JSON format", {
                    status: 500,
                    headers: { "Content-Type": "text/plain; charset=utf-8" },
                });
            }
        } else {
            return new Response("Invalid AUTH_USERS format", {
                status: 500,
                headers: { "Content-Type": "text/plain; charset=utf-8" },
            });
        }

        const url = new URL(request.url);
        const pathname = url.pathname;

        // 1. POST /api/login
        if (pathname === "/api/login" && request.method === "POST") {
            try {
                const body = await request.json();
                const { username, password, remember } = body || {};

                if (
                    username &&
                    typeof username === "string" &&
                    password &&
                    typeof password === "string" &&
                    Object.prototype.hasOwnProperty.call(USERS, username) &&
                    USERS[username] === password
                ) {
                    // Max-Age: 30 days if remember is true, otherwise 12 hours
                    const maxAgeSec = remember ? 30 * 86400 : 12 * 3600;
                    const token = await createToken(username, maxAgeSec, secretKeyStr);
                    const cookie = `auth_token=${token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${maxAgeSec}`;

                    return new Response(
                        JSON.stringify({ success: true, user: username }),
                        {
                            status: 200,
                            headers: {
                                "Content-Type": "application/json; charset=utf-8",
                                "Set-Cookie": cookie,
                            },
                        }
                    );
                }
            } catch (err) {}

            return new Response(
                JSON.stringify({
                    success: false,
                    message: "اسم المستخدم أو كلمة المرور غير صحيحة",
                }),
                {
                    status: 401,
                    headers: { "Content-Type": "application/json; charset=utf-8" },
                }
            );
        }

        // 2. GET /api/session
        if (pathname === "/api/session" && request.method === "GET") {
            const token = getCookie(request, "auth_token");
            const user = await verifyToken(token, secretKeyStr, USERS);
            if (user) {
                return new Response(
                    JSON.stringify({ authenticated: true, user }),
                    {
                        status: 200,
                        headers: { "Content-Type": "application/json; charset=utf-8" },
                    }
                );
            }
            return new Response(
                JSON.stringify({ authenticated: false }),
                {
                    status: 401,
                    headers: { "Content-Type": "application/json; charset=utf-8" },
                }
            );
        }

        // 3. POST /api/logout & GET /api/logout
        if (pathname === "/api/logout" && (request.method === "POST" || request.method === "GET")) {
            const clearCookie = "auth_token=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0";
            const headers = new Headers();
            headers.set("Set-Cookie", clearCookie);

            if (request.method === "POST" && request.headers.get("Accept")?.includes("application/json")) {
                headers.set("Content-Type", "application/json; charset=utf-8");
                return new Response(JSON.stringify({ success: true, redirect: "/" }), {
                    status: 200,
                    headers,
                });
            }

            headers.set("Location", "/");
            return new Response(null, { status: 302, headers });
        }

        // 4. Route Protection Middleware
        const token = getCookie(request, "auth_token");
        const user = await verifyToken(token, secretKeyStr, USERS);

        // Public routes: allow the root portal and index.html so the login screen can load
        const isPublic = pathname === "/" || pathname === "/index.html" || pathname === "/favicon.ico";

        if (!user && !isPublic) {
            // Unauthenticated user attempting to access protected sub-routes (/ahsa/*, /RiyadhPlazas/*, /forms/*, etc.)
            return new Response(null, {
                status: 302,
                headers: { Location: "/" },
            });
        }

        // Authenticated user or public login screen: serve static asset
        return await env.ASSETS.fetch(request);
    },
};
