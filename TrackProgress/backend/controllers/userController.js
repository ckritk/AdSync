const User = require('../models/User');

// Create or get existing user by username
exports.loginUser = async (req, res) => {
  const { username } = req.body;

  if (!username) {
    return res.status(400).json({ error: 'Username is required' });
  }

  try {
    let user = await User.findOne({ username });

    if (!user) {
      user = new User({ username });
      await user.save();
    }

    res.json({ success: true, userId: user._id, username: user.username });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
};


exports.getUserCampaigns = async (req, res) => {
    const { userId } = req.params;
  
    try {
      const user = await User.findById(userId).populate('campaigns');
  
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }
  
      res.json({ campaigns: user.campaigns });
    } catch (err) {
      res.status(500).json({ error: 'Failed to fetch campaigns' });
    }
  };