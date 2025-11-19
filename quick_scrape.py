"""
QUICK START SCRIPT - Twitter/X Scraper
Run this script to quickly scrape your Twitter data!
"""

from scrape_twitter_selenium import SeleniumTwitterScraper
import os

def quick_scrape():
    """Quick scrape with simple options"""
    print("=" * 70)
    print("      QUICK TWITTER/X SCRAPER FOR POST TRACKER")
    print("=" * 70)
    
    # Auto-detect file format
    excel_file = None
    if os.path.exists('Post Tracker.xlsx'):
        excel_file = 'Post Tracker.xlsx'
        print("\n✓ Found: Post Tracker.xlsx")
    elif os.path.exists('Post Tracker.csv'):
        excel_file = 'Post Tracker.csv'
        print("\n✓ Found: Post Tracker.csv")
    else:
        print("\n❌ ERROR: Cannot find 'Post Tracker.xlsx' or 'Post Tracker.csv'")
        print("   Please make sure your file is in the same folder as this script.")
        return
    
    print(f"\nThis will scrape data from the Twitter/X links in '{excel_file}'")
    print("\n📋 Data that will be extracted:")
    print("   • Tweet text/content")
    print("   • Likes, Retweets, Replies, Views")
    print("   • Username and timestamp")
    print("   • Media detection (images/videos)")
    print("\n⏱️  Time estimate: ~3-5 seconds per tweet")
    print("\n" + "=" * 70)
    
    # Quick menu
    print("\n🎯 QUICK OPTIONS:")
    print("   [1] Test Mode - Scrape first 3 tweets (RECOMMENDED to start)")
    print("   [2] Small Batch - Scrape first 20 tweets")
    print("   [3] Medium Batch - Scrape first 50 tweets")
    print("   [4] All Tweets - Scrape everything in the file")
    print("   [5] Custom - Choose your own range")
    print("   [Q] Quit")
    
    choice = input("\n👉 Enter your choice: ").strip().upper()
    
    if choice == 'Q':
        print("\n👋 Goodbye!")
        return
    
    # Initialize scraper
    scraper = SeleniumTwitterScraper(excel_file, headless=False)
    scraper.load_excel()
    
    total_rows = len(scraper.df)
    print(f"\n📊 Your Excel file has {total_rows} total rows")
    
    # Process based on choice
    results = None
    
    if choice == '1':
        print("\n🧪 TEST MODE: Scraping first 3 tweets...")
        results = scraper.process_links(sample_size=3)
    
    elif choice == '2':
        print("\n📦 SMALL BATCH: Scraping first 20 tweets...")
        results = scraper.process_links(sample_size=20)
    
    elif choice == '3':
        print("\n📦 MEDIUM BATCH: Scraping first 50 tweets...")
        results = scraper.process_links(sample_size=50)
    
    elif choice == '4':
        confirm = input(f"\n⚠️  This will scrape ALL {total_rows} tweets. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            print(f"\n🚀 FULL SCRAPE: Processing all {total_rows} tweets...")
            print("⏱️  This may take a while. You can stop with Ctrl+C")
            results = scraper.process_links()
        else:
            print("\n❌ Cancelled")
            return
    
    elif choice == '5':
        print("\n📝 CUSTOM RANGE")
        try:
            start = int(input(f"   Start row (0 to {total_rows-1}): "))
            end = int(input(f"   End row (1 to {total_rows}): "))
            
            if start < 0 or end > total_rows or start >= end:
                print("❌ Invalid range!")
                return
            
            print(f"\n🎯 CUSTOM: Scraping rows {start} to {end-1}...")
            results = scraper.process_links(start_row=start, end_row=end)
        except ValueError:
            print("❌ Invalid input!")
            return
    
    else:
        print("\n❌ Invalid choice!")
        return
    
    # Save results
    if results:
        output_file = scraper.save_results(results)
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Your data has been scraped!")
        print("=" * 70)
        print(f"\n📁 Output file: {output_file}")
        print("\n💡 TIP: Open the output file in Excel to see your scraped data!")
        print("=" * 70)
    else:
        print("\n❌ No results to save.")


if __name__ == "__main__":
    try:
        quick_scrape()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user.")
        print("💾 Partial results may have been saved.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("\n💡 Tips:")
        print("   • Make sure 'Post Tracker.xlsx' is in the same folder")
        print("   • Make sure Chrome browser is installed")
        print("   • Check that you have internet connection")
