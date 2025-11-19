# Quick Start Guide - Enhanced Twitter Scraper

## 🚀 Quick Run Instructions

### Step 1: Prepare Your Environment
```bash
# Make sure you have the required packages
pip install selenium pandas openpyxl
```

### Step 2: Ensure Your CSV File is Ready
- File name: `Post Tracker.csv` (in the same directory)
- First column should contain Twitter/X URLs

### Step 3: Run the Script
```bash
python scrape_twitter_selenium.py
```

### Step 4: Choose Your Option
When prompted, select:
- **Option 1**: Test with 3 posts (recommended for first run)
- **Option 2**: Test with 10 posts
- **Option 3**: Process all posts
- **Option 4**: Custom range

---

## 📊 What Gets Scraped

For each post URL, the script collects:

### Post Information
- ✅ Tweet text
- ✅ Likes, Retweets, Replies
- ✅ **NEW:** View count
- ✅ Timestamp
- ✅ **NEW:** Video detection (1 = has video, 0 = no video)

### Account Information (from user profile)
- ✅ **NEW:** Display name
- ✅ **NEW:** Follower count
- ✅ **NEW:** Account creation date

---

## 📁 Output File

The script creates a new file with timestamp:
```
Post Tracker_scraped_20251119_120050.csv
```

This file contains all original columns PLUS new columns:
- `Views`
- `Replies`
- `Has Video`
- `Followers`
- `Account Created`
- `Account Name`

---

## ⏱️ Expected Time

**Per Post:** ~5-8 seconds
- 2-3 seconds: Scrape post data
- 3-5 seconds: Visit profile and scrape account info

**For 100 posts:** ~8-13 minutes

---

## 🔍 Monitoring Progress

Watch the console output for real-time progress:
```
[1/10] Processing: https://x.com/username/status/123456789
    Loading page...
    ✓ Extracted text: This is a tweet...
    ✓ Engagement - Likes: 150, Retweets: 25, Replies: 8, Views: 12500
    ✓ Media - Images: False, Video: 1
    Extracting profile information for @username...
      ✓ Account name: John Doe
      ✓ Followers: 15000
      ✓ Account created: January 2020
    ✓ Successfully scraped tweet
```

---

## ⚠️ Important Tips

1. **First Time:** Always test with 3 posts first (Option 1)
2. **Browser Window:** A Chrome window will open - don't close it manually
3. **Manual Login:** If prompted to log in to Twitter/X, do so in the browser window
4. **Rate Limiting:** If you get rate limited, wait 15 minutes and try again
5. **Error Handling:** Failed posts are marked but won't stop the entire process

---

## 🐛 Troubleshooting

### "ChromeDriver not found"
```bash
pip install webdriver-manager
```

### "Cannot find file 'Post Tracker.csv'"
- Ensure the CSV file is in the same directory as the script
- Check the file name is exactly `Post Tracker.csv`

### "Timeout loading page"
- Twitter may be slow or blocking requests
- Try running again with fewer posts
- Consider logging into Twitter/X manually when browser opens

### Script stops unexpectedly
- Check your internet connection
- Verify Twitter/X is accessible
- Restart and use a smaller batch size

---

## 📈 Data Validation

After scraping, check your output file for:
- ✅ View counts populated
- ✅ Follower counts present
- ✅ Video field shows 0 or 1
- ✅ Account creation dates visible

---

## 🎯 Best Practices

1. **Start Small:** Test with 3-5 posts first
2. **Monitor First Run:** Watch the browser to ensure it's working correctly
3. **Check Output:** Verify data quality before processing large batches
4. **Regular Breaks:** For large datasets, consider breaking into batches of 50-100
5. **Save Progress:** The script auto-saves, but consider backing up output files

---

## 📞 Need Help?

Common issues and solutions:
- **No views showing:** Some posts don't display view counts publicly
- **Profile data missing:** Account may be private or suspended
- **Slow performance:** Normal - profile scraping adds extra time
- **Rate limited:** Wait 15-30 minutes before retrying

---

## ✨ Success Indicator

At the end, you should see:
```
Summary:
  Total processed: 10
  Successful: 10
  Failed: 0

Data Collected:
  Posts with videos: 3
  Posts with view counts: 9
  Profiles scraped: 10

✓ Saved to: Post Tracker_scraped_20251119_120050.csv
```

---

**Ready to start? Run:** `python scrape_twitter_selenium.py`
