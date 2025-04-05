// controllers/urlController.js
const shortid = require('shortid');
const geoip = require('geoip-lite');
const Url = require('../models/Url');

// Helper: Extract client details
function extractClientDetails(req) {
  const ua = req.headers['user-agent'] || '';
  const ipAddress = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
  const geo = geoip.lookup(ipAddress);
  const location = geo ? `${geo.city || 'Unknown'}, ${geo.country || 'Unknown'}` : 'Unknown';

  const isBot = /bot|crawl|spider/i.test(ua);

  let browser = 'Unknown';
  if (ua.includes('Chrome')) browser = 'Chrome';
  else if (ua.includes('Firefox')) browser = 'Firefox';
  else if (ua.includes('Safari') && !ua.includes('Chrome')) browser = 'Safari';
  else if (ua.includes('Edge')) browser = 'Edge';
  else if (ua.includes('MSIE') || ua.includes('Trident')) browser = 'Internet Explorer';

  let os = 'Unknown';
  if (ua.includes('Windows')) os = 'Windows';
  else if (ua.includes('Mac OS')) os = 'Mac';
  else if (ua.includes('Android')) os = 'Android';
  else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS';
  else if (ua.includes('Linux')) os = 'Linux';

  let deviceType = 'Desktop';
  if (/Mobi|Android|iPhone|iPad/i.test(ua)) deviceType = 'Mobile';

  return {
    ipAddress,
    deviceType,
    browser,
    os,
    location,
    isBot
  };
}

exports.createShortUrl = async (req, res) => {
  const { originalUrl, name } = req.body;
  const shortId = shortid.generate();

  try {
    const newUrl = new Url({
      originalUrl,
      shortId,
      name
    });

    await newUrl.save();
    res.json({ shortUrl: `${process.env.BASE_URL}/${shortId}` });
  } catch (error) {
    res.status(500).json({ error: 'Error creating short URL' });
  }
};

exports.handleRedirect = async (req, res) => {
  const { shortId } = req.params;

  try {
    const url = await Url.findOne({ shortId });
    if (!url) return res.status(404).json({ error: 'URL not found' });

    const clientDetails = extractClientDetails(req);
    url.clicks += 1;
    url.logs.push({
      timestamp: new Date(),
      referrer: req.get('Referer') || 'Direct',
      sessionId: req.sessionID || 'Unknown',
      ...clientDetails
    });
    await url.save();

    res.redirect(url.originalUrl);
  } catch (error) {
    res.status(500).json({ error: 'Error redirecting' });
  }
};

exports.getUrlStats = async (req, res) => {
    const { id } = req.params;
    try {
      const url = await Url.findById(id);
      if (!url) {
        return res.status(404).json({ error: "URL not found" });
      }
  
      // Just return the logs array (you can filter fields if needed)
      res.json({ clicks: url.logs });
    } catch (err) {
      res.status(500).json({ error: "Server error" });
    }
  };
  