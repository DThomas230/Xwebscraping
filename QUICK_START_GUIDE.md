# 🚀 QUICK START GUIDE

## How to Use Your Twitter/X Scraper

### ⚡ EASIEST METHOD (Double-Click!)

1. **Double-click** `RUN_SCRAPER.bat` in Windows Explorer
2. Choose an option from the menu
3. Wait for the browser to open and scrape the data
4. Your results will be saved automatically!

### 📋 What Gets Scraped

From each Twitter/X link in your Excel file, the script will extract:

| Data Field | Description |
|------------|-------------|
| **Text** | The tweet content/message |
| **Likes** | Number of likes ❤️ |
| **Retweets** | Number of retweets 🔄 |
| **Replies** | Number of replies 💬 |
| **Views** | Number of views 👁️ |
| **Username** | Twitter handle |
| **Timestamp** | When it was posted |
| **Media** | If it has images/videos |

### 📂 Files Overview

```
Your Project Folder/
│
├── Post Tracker.xlsx           ← Your original Excel file with links
│
├── RUN_SCRAPER.bat            ← 🎯 DOUBLE-CLICK THIS to start!
├── quick_scrape.py            ← Easy-to-use scraper script
│
├── scrape_twitter_selenium.py ← Main scraper (advanced)
├── scrape_twitter_data.py     ← Alternative scraper
│
├── README.md                  ← Full documentation
└── QUICK_START_GUIDE.md       ← This file!
```

### 🎯 Step-by-Step Instructions

#### For Beginners:

1. **Make sure your Excel file is named:** `Post Tracker.xlsx`
   - It should be in the same folder as these scripts
   - The first column should contain Twitter/X links

2. **Run the scraper:**
   - **Method 1 (Easiest):** Double-click `RUN_SCRAPER.bat`
   - **Method 2:** Open PowerShell here and type: `python quick_scrape.py`

3. **Choose an option:**
   ```
   [1] Test Mode - Try first 3 tweets (START HERE! ✅)
   [2] Small Batch - Scrape 20 tweets
   [3] Medium Batch - Scrape 50 tweets
   [4] All Tweets - Scrape everything
   [5] Custom Range - You pick the rows
   ```

4. **Browser opens automatically:**
   - Chrome will open and start visiting each Twitter link
   - You'll see it working in real-time! 
   - If you see a login page, you can log in (optional)

5. **Wait for completion:**
   - Each tweet takes ~3-5 seconds
   - Progress is shown in the console
   - You can stop anytime with `Ctrl + C`

6. **Find your results:**
   - New file created: `Post Tracker_scraped_YYYYMMDD_HHMMSS.xlsx`
   - Open it in Excel to see all the scraped data!

### ⏱️ Time Estimates

| Tweets | Estimated Time |
|--------|---------------|
| 3 (test) | ~15 seconds |
| 20 | ~2 minutes |
| 50 | ~4-5 minutes |
| 100 | ~8-10 minutes |

*Times may vary based on internet speed and Twitter's response time*

### ✅ First Time Testing

**IMPORTANT: Always test first!**

1. Run option [1] to test with 3 tweets
2. Check the output file to verify data looks correct
3. If good, proceed with larger batches
4. If issues, check troubleshooting below

### ❓ Troubleshooting

#### "No module named 'selenium'"
```powershell
pip install selenium webdriver-manager
```

#### "Chrome not found"
- Install Google Chrome browser
- Make sure it's the latest version

#### Browser opens but nothing happens
- Check your internet connection
- Try logging into Twitter/X when browser opens
- Some tweets may be deleted or private

#### "Post Tracker.xlsx not found"
- Make sure the file is in the same folder
- Check the file name is exactly: `Post Tracker.xlsx`

#### Not getting likes/retweets
- Twitter may be blocking the scraper
- Try logging in when browser opens
- Some data may not be publicly available

#### Scraper is too slow
- This is normal! Twitter has rate limits
- Don't remove the delays or you'll get blocked
- Consider processing in smaller batches

### 🎓 Tips for Best Results

1. **Start Small:** Always test with 3-5 tweets first
2. **Login Optional:** Log into Twitter for better access (but not required for public tweets)
3. **Be Patient:** Each tweet takes a few seconds - don't rush!
4. **Backup Data:** Keep your original Excel file safe
5. **Check Output:** Verify the scraped data makes sense
6. **Batch Processing:** For 100+ tweets, do them in batches of 50

### 🔧 Advanced Usage

If you want more control, you can edit `quick_scrape.py`:

```python
# Change delay between tweets (default is 2 seconds)
time.sleep(2)  # Change to 3 or 4 if getting blocked

# Run in headless mode (no browser window)
scraper = SeleniumTwitterScraper('Post Tracker.xlsx', headless=True)
```

### 📊 Understanding the Output

Your output Excel file will have these NEW columns added:

- `Username` - @handle
- `Display Name` - Full name
- `Text` - Tweet content
- `Likes` - Number of likes
- `Retweets` - Number of retweets
- `Replies` - Number of replies
- `Views` - View count
- `Has Media` - True/False
- `Has Image` - True/False
- `Has Video` - True/False
- `Timestamp` - When posted
- `Status` - Success/error status

The original columns from your Excel file are preserved!

### ⚠️ Important Notes

- **Twitter Limits:** Twitter actively blocks scrapers. The script includes delays to avoid this.
- **Login:** Some tweets need login. The browser stays open so you can log in manually.
- **Deleted Tweets:** If a tweet is deleted, the scraper will skip it.
- **Rate Limits:** Don't scrape too fast or you'll be temporarily blocked.

### 🆘 Need Help?

1. Read the full `README.md` for detailed documentation
2. Check that all requirements are installed:
   ```powershell
   pip install pandas openpyxl selenium webdriver-manager requests beautifulsoup4
   ```
3. Make sure Chrome browser is installed and up to date
4. Try with a smaller batch first (option 1 - test mode)

### 🎉 You're Ready!

Double-click `RUN_SCRAPER.bat` and choose option 1 to get started!

---

**Questions?** Check the `README.md` file for more detailed information.

**Happy Scraping! 🚀**
