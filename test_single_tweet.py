"""
Quick test script for debugging a single tweet
"""
from scrape_twitter_selenium import SeleniumTwitterScraper
import pandas as pd

# Test URL
test_url = "https://x.com/jacksonhinklle/status/1714660808821538841"

print("=" * 70)
print("TESTING SINGLE TWEET")
print("=" * 70)
print(f"\nURL: {test_url}")
print("\n" + "=" * 70)

# Create a simple CSV with just this URL
test_df = pd.DataFrame({'Post_URL': [test_url]})
test_df.to_csv('test_single.csv', index=False)

# Initialize scraper
scraper = SeleniumTwitterScraper('test_single.csv', headless=False)
scraper.load_excel()

# Setup driver
if scraper.setup_driver():
    # Extract info
    print("\nExtracting tweet information...")
    data = scraper.extract_tweet_info(test_url)
    
    # Close browser
    scraper.driver.quit()
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    if data:
        print(f"Username: {data.get('username')}")
        print(f"Account Name: {data.get('account_name')}")
        print(f"Text: {data.get('text', '')[:100]}...")
        print(f"\nENGAGEMENT METRICS:")
        print(f"  Likes: {data.get('likes')}")
        print(f"  Retweets: {data.get('retweets')}")
        print(f"  Replies: {data.get('replies')}")
        print(f"  Views: {data.get('views')} ⭐")
        print(f"  Bookmarks: {data.get('bookmarks')}")
        print(f"\nACCOUNT INFO:")
        print(f"  Followers: {data.get('followers')}")
        print(f"  Account Created: {data.get('account_created')}")
        print(f"\nMEDIA:")
        print(f"  Has Video: {data.get('has_video')}")
        print(f"  Has Image: {data.get('has_image')}")
        print(f"\nStatus: {data.get('status')}")
    else:
        print("No data extracted!")
    
    print("\n" + "=" * 70)
else:
    print("Failed to setup driver!")
