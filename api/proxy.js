export const config = { api: { bodyParser: true } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  const endpoint = req.query.endpoint;
  if (!endpoint) return res.status(400).json({ error: 'Missing endpoint' });

  const url = `https://kosherwithoutborders.com/KWB/api/${endpoint}`;
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body || {})
    });
    const text = await r.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    res.status(r.status).json(data);
  } catch(e) {
    res.status(500).json({ error: e.message, stack: e.stack });
  }
}
