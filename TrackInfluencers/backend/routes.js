// routes.js
const express = require('express');
const router = express.Router();
const urlController = require('./controllers/urlController');
const userController = require('./controllers/userController');
const campaignController = require('./controllers/campaignController');

router.post('/user/login', userController.loginUser);
router.get('/user/:userId/campaigns', userController.getUserCampaigns);

router.post('/url/shorten', urlController.createShortUrl);
router.get('/url/:shortId', urlController.handleRedirect);
router.get('/url/stats/:id', urlController.getUrlStats);

router.post('/campaign/create', campaignController.createCampaign);
router.get('/campaign/:id', campaignController.getCampaignDetails);
router.post('/campaign/addinfluencer', campaignController.addInfluencer);
router.post('/campaign/addurl', campaignController.addUrl);
router.post('/campaign/add-influencer', campaignController.addInfluencerToCampaign);

module.exports = router;
