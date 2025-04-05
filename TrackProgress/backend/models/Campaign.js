const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const campaignSchema = new Schema({
  name: { type: String, required: true },
  campaignUrls: [{ type: Schema.Types.ObjectId, ref: 'Url' }],
  conversionUrls: [{ type: Schema.Types.ObjectId, ref: 'Url' }],
  influencers: [
    {
      influencer: { type: Schema.Types.ObjectId, ref: 'Influencer', required: true },
      status: { type: String, enum: ['accepted', 'rejected', 'pending'], default: 'pending' }
    }
  ]
});

module.exports = mongoose.model('Campaign', campaignSchema);
