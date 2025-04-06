const mongoose = require('mongoose');
const faker = require('faker');
require('dotenv').config();

const Url = require('./models/Url');

const shortIds = [
  'wkd4gt',
  'vh0e5',
  'yzhup',
  'xeyti'
];

const shortIds1 = [ 'xk4t74' ]

const socialMedia = [
  'https://www.facebook.com',
  'https://www.twitter.com',
  'https://www.instagram.com',
  'https://www.linkedin.com',
  'https://www.pinterest.com',
  'https://www.reddit.com',
  'https://www.tumblr.com'
];

const deviceTypes = ['Desktop', 'Mobile', 'Tablet'];
const browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'];
const osList = ['Windows', 'macOS', 'Linux', 'Android', 'iOS'];

mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.error('DB connection error:', err));

async function simulateClicks() {
  for (const shortId of shortIds) {
    try {
      const url = await Url.findOne({ shortId });
      if (!url) continue;

      // Generate 40-50 random logs
      const numClicks = Math.floor(Math.random() * 61) + 20; // 20 to 80 clicks
      const newLogs = [];

      for (let i = 0; i < numClicks; i++) {
        const clickData = {
          timestamp: faker.date.recent(),
          referrer: socialMedia[Math.floor(Math.random() * socialMedia.length)],
          userAgent: faker.internet.userAgent(),
          ipAddress: faker.internet.ip(),
          deviceType: deviceTypes[Math.floor(Math.random() * deviceTypes.length)],
          browser: browsers[Math.floor(Math.random() * browsers.length)],
          os: osList[Math.floor(Math.random() * osList.length)],
          location: faker.address.country(),
          source: 'Simulated',
          sessionId: faker.datatype.uuid(),
          isBot: faker.datatype.boolean()
        };
        newLogs.push(clickData);
      }

      // Update clicks and logs in one operation
      url.clicks += numClicks;
      url.logs.push(...newLogs);
      await url.save();

      console.log(`Simulated ${numClicks} clicks for ${shortId}`);
    } catch (error) {
      console.error(`Error simulating clicks for ${shortId}:`, error.message);
    }
  }
  console.log('Click simulation completed.');
  mongoose.connection.close();
}

simulateClicks();
