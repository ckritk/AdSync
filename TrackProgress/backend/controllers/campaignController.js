const Campaign = require('../models/Campaign');
const User = require('../models/User');
const Url = require('../models/Url');
const Influencer = require('../models/Influencer');

exports.createCampaign = async (req, res) => {
  const { name, userId } = req.body;

  if (!name || !userId) {
    return res.status(400).json({ error: 'Name and userId are required' });
  }

  try {
    const newCampaign = new Campaign({
      name,
      campaignUrls: [],
      conversionUrls: [],
      influencers: []
    });

    await newCampaign.save();

    await User.findByIdAndUpdate(userId, {
      $push: { campaigns: newCampaign._id }
    });

    res.json({ success: true, campaign: newCampaign });
  } catch (err) {
    res.status(500).json({ error: 'Failed to create campaign' });
  }
};

exports.getCampaignDetails = async (req, res) => {
  const { id } = req.params;

  try {
    const campaign = await Campaign.findById(id)
      .populate('campaignUrls')
      .populate('conversionUrls')
      .populate('influencers.influencer');

    if (!campaign) {
      return res.status(404).json({ error: 'Campaign not found' });
    }

    res.json({ campaign });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch campaign details' });
  }
};

exports.addInfluencer = async (req, res) => {
  const { name, campaignId } = req.body;

  if (!name || !campaignId) {
    return res.status(400).json({ error: 'Name and campaignId are required' });
  }

  try {
    const influencer = new Influencer({ name });
    await influencer.save();

    const campaign = await Campaign.findByIdAndUpdate(
      campaignId,
      { $push: { influencers: { influencer: influencer._id, status: 'pending' } } },
      { new: true }
    );

    if (!campaign) {
      return res.status(404).json({ error: 'Campaign not found' });
    }

    res.json({ message: 'Influencer added', influencer });
  } catch (err) {
    res.status(500).json({ error: 'Error adding influencer' });
  }
};

exports.addUrl = async (req, res) => {
  const { name, originalUrl, campaignId, type } = req.body;

  if (!name || !originalUrl || !campaignId || !type) {
    return res.status(400).json({ error: 'All fields are required' });
  }

  try {
    const url = new Url({
      name,
      originalUrl,
      shortId: Math.random().toString(36).substring(7)
    });

    await url.save();

    const updateField = type === 'campaign' ? 'campaignUrls' : 'conversionUrls';

    await Campaign.findByIdAndUpdate(campaignId, {
      $push: { [updateField]: url._id }
    });

    res.json({ message: 'URL added', url });
  } catch (err) {
    res.status(500).json({ error: 'Error adding URL' });
  }
};

exports.addInfluencerToCampaign = async (req, res) => {
  const { campaignId, influencerId } = req.body;

  if (!campaignId || !influencerId) {
    return res.status(400).json({ error: 'campaignId and influencerId are required.' });
  }

  try {
    const campaign = await Campaign.findById(campaignId);

    if (!campaign) {
      return res.status(404).json({ error: 'Campaign not found.' });
    }

    // Check if influencer already exists in campaign
    const alreadyExists = campaign.influencers.some(
      (entry) => entry.influencer.toString() === influencerId
    );

    if (alreadyExists) {
      return res.status(400).json({ error: 'Influencer already added to this campaign.' });
    }

    // Add influencer with status 'pending'
    campaign.influencers.push({
      influencer: influencerId,
      status: 'pending',
    });

    await campaign.save();

    res.status(200).json({ message: 'Influencer added to campaign with status pending.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
};