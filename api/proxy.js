export const config = { api: { bodyParser: true } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  const endpoint = req.query.endpoint;
  if (!endpoint) return res.status(400).json({ error: 'Missing endpoint' });

  const isGetPlaces = endpoint.includes("GetPlaces");
  const base = isGetPlaces ? "https://kosherwithoutborders.com/KWB-API/api/" : "https://kosherwithoutborders.com/KWB/api/";
  const url = base + endpoint;

  // Inject KWB API token if placeholder present
  let body = req.body || {};
  if (body.idToken === '__KWB_TOKEN__') {
    body = { ...body, idToken: process.env.KWB_API_TOKEN || '' };
  }

  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const text = await r.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    res.status(r.status).json(data);
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
}
