# AdSync

Brands struggle to find influencers whose niche aligns with their audience and values. Post scheduling is manual and error-prone, and tracking the real impact—traffic, conversions, or sales—is nearly impossible.
This platform helps brands and influencers collaborate seamlessly by:
- Matching the right influencers based on niche and brand fit
- Automating post scheduling across campaigns
- Tracking campaign progress 
Built to save time, improve targeting, and deliver measurable results.


## Smart Influencer Matching
Uses filtering and K-Means clustering on influencer data to recommend niche-aligned influencers for brands.

## Automated Post Scheduling:
Users select platform, upload media, set captions and schedule posts. Media is stored in Google Drive, and posts are auto-published via the Graph API using a background scheduler.

## Campaign Tracking with Short URLs:
Generates campaign and conversion links, tracks clicks via a redirect handler, and stores data in MongoDB. A dashboard visualizes click patterns and conversion rates.
