const mongoose = require('mongoose');

const urlSchema = new mongoose.Schema({
  name: { type: String }, 
  type: { type: String },
  originalUrl: { type: String, required: true },
  shortId: { type: String, required: true, unique: true },
  clicks: { type: Number, default: 0 },
  logs: [{
    timestamp: { type: Date, default: Date.now },
    referrer: String,
    userAgent: String,
    ipAddress: String,
    deviceType: String,
    browser: String,
    os: String,
    location: String,
    source: String,
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    sessionId: String,
    isBot: { type: Boolean, default: false }
  }]
});

module.exports = mongoose.model('Url', urlSchema);
