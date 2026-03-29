export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  const endpoint = req.query.endpoint;
  const url = `https://kosherwithoutborders.com/KWB/api/${endpoint}`;
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const data = await r.json();
    res.status(r.status).json(data);
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
}
EOFcd ~/Downloads/kwb-portal-repo && git add -A && git commit -m "add vercel proxy to bypass CORS" && git pushcat > ~/Downloads/kwb-portal-repo/vercel.json << 'EOF'
{
  "functions": {
    "api/proxy.js": { "memory": 128, "maxDuration": 10 }
  }
}
EOFcat > ~/Downloads/kwb-portal-repo/vercel.json << 'EOF'
{
  "functions": {
    "api/proxy.js": { "memory": 128, "maxDuration": 10 }
  }
}
