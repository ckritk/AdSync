const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const userSchema = new Schema({
  username: { type: String, required: true },
  campaigns: [{ type: Schema.Types.ObjectId, ref: 'Campaign' }],
});

module.exports = mongoose.model('User', userSchema);
