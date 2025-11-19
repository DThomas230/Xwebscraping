"""
Twitter/X Web Scraping Script for Post Tracker
This script scrapes data from Twitter/X posts and fills the Excel spreadsheet
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import json

class TwitterScraper:
    def __init__(self, excel_file='Post Tracker.xlsx'):
        self.excel_file = excel_file
        self.df = None
        self.is_csv = excel_file.lower().endswith('.csv')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def load_excel(self):
        """Load the Excel or CSV file"""
        print(f"Loading {'CSV' if self.is_csv else 'Excel'} file...")
        
        if self.is_csv:
            self.df = pd.read_csv(self.excel_file)
        else:
            self.df = pd.read_excel(self.excel_file)
        
        # Rename columns for easier access
        # The first column has a link as its name, so we'll rename it
        if self.df.columns[0] != 'Post_URL':
            columns = ['Post_URL'] + [f'Column_{i}' for i in range(1, len(self.df.columns))]
            self.df.columns = columns
        
        print(f"Loaded {len(self.df)} rows")
        return self.df
    
    def extract_tweet_id(self, url):
        """Extract tweet ID from URL"""
        if pd.isna(url) or not isinstance(url, str):
            return None
        
        # Pattern to extract tweet ID from various Twitter/X URL formats
        patterns = [
            r'/status/(\d+)',
            r'/statuses/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def scrape_tweet_data(self, url, retry_count=3):
        """
        Scrape data from a Twitter/X post
        
        Note: Twitter/X has heavy anti-scraping measures. This method tries to extract
        basic information, but may require authentication or alternative methods for full data.
        """
        if pd.isna(url) or not isinstance(url, str):
            return None
        
        tweet_id = self.extract_tweet_id(url)
        if not tweet_id:
            print(f"  ✗ Could not extract tweet ID from: {url}")
            return None
        
        print(f"  Scraping tweet ID: {tweet_id}")
        
        # Try different approaches
        data = {
            'url': url,
            'tweet_id': tweet_id,
            'username': None,
            'text': None,
            'likes': None,
            'retweets': None,
            'replies': None,
            'views': None,
            'timestamp': None,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Approach 1: Try to scrape the page directly
        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to extract username from URL
                    username_match = re.search(r'x\.com/([^/]+)/', url)
                    if username_match:
                        data['username'] = username_match.group(1)
                    
                    # Try to find tweet text in meta tags
                    og_description = soup.find('meta', property='og:description')
                    if og_description:
                        data['text'] = og_description.get('content', '')[:500]  # First 500 chars
                    
                    # Try to find tweet title
                    og_title = soup.find('meta', property='og:title')
                    if og_title and not data['text']:
                        data['text'] = og_title.get('content', '')
                    
                    print(f"    ✓ Successfully scraped (attempt {attempt + 1})")
                    break
                    
                elif response.status_code == 429:
                    print(f"    ⚠ Rate limited. Waiting before retry...")
                    time.sleep(5 * (attempt + 1))
                    
                else:
                    print(f"    ✗ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2)
        
        # Small delay between requests
        time.sleep(1)
        
        return data
    
    def process_all_links(self, start_row=0, end_row=None, sample_size=None):
        """
        Process all links in the Excel file
        
        Args:
            start_row: Starting row index (0-based)
            end_row: Ending row index (exclusive), None for all rows
            sample_size: If provided, only process this many rows (for testing)
        """
        if self.df is None:
            self.load_excel()
        
        # Determine which rows to process
        if sample_size:
            end_row = min(start_row + sample_size, len(self.df))
        elif end_row is None:
            end_row = len(self.df)
        
        print(f"\nProcessing rows {start_row} to {end_row-1} ({end_row - start_row} rows)")
        print("=" * 70)
        
        results = []
        
        for idx in range(start_row, end_row):
            url = self.df.iloc[idx]['Post_URL']
            
            print(f"\n[{idx + 1}/{end_row}] Processing: {url}")
            
            if pd.isna(url) or not isinstance(url, str) or 'http' not in url:
                print("  ⊘ Skipping (no valid URL)")
                results.append(None)
                continue
            
            data = self.scrape_tweet_data(url)
            results.append(data)
        
        return results
    
    def save_results(self, results, output_file=None):
        """Save the scraped results back to Excel or CSV"""
        if output_file is None:
            # Create a new filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_ext = '.csv' if self.is_csv else '.xlsx'
            output_file = f'Post Tracker_scraped_{timestamp}{file_ext}'
        
        print(f"\nSaving results to: {output_file}")
        
        # Create a results DataFrame
        results_df = pd.DataFrame([r for r in results if r is not None])
        
        if len(results_df) > 0:
            # Add the scraped data as new columns
            self.df['Username'] = results_df['username'].values if 'username' in results_df else None
            self.df['Tweet_Text'] = results_df['text'].values if 'text' in results_df else None
            self.df['Likes'] = results_df['likes'].values if 'likes' in results_df else None
            self.df['Retweets'] = results_df['retweets'].values if 'retweets' in results_df else None
            self.df['Replies'] = results_df['replies'].values if 'replies' in results_df else None
            self.df['Views'] = results_df['views'].values if 'views' in results_df else None
            self.df['Timestamp'] = results_df['timestamp'].values if 'timestamp' in results_df else None
            self.df['Scraped_At'] = results_df['scraped_at'].values if 'scraped_at' in results_df else None
        
        # Save to CSV or Excel
        if self.is_csv:
            self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            self.df.to_excel(output_file, index=False)
        print(f"✓ Saved {len(self.df)} rows to {output_file}")
        
        return output_file


def main():
    """Main execution function"""
    print("=" * 70)
    print("TWITTER/X WEB SCRAPING SCRIPT")
    print("=" * 70)
    print("\n⚠ IMPORTANT NOTES:")
    print("  - Twitter/X has strict anti-scraping measures")
    print("  - This script may have limited success without authentication")
    print("  - Consider using Twitter API or browser automation (Selenium) for better results")
    print("  - Rate limiting may occur - the script includes delays to minimize this")
    print("\n" + "=" * 70)
    
    # Auto-detect file format
    import os
    if os.path.exists('Post Tracker.csv'):
        data_file = 'Post Tracker.csv'
    else:
        data_file = 'Post Tracker.xlsx'
    
    print(f"\nUsing file: {data_file}")
    
    # Initialize scraper
    scraper = TwitterScraper(data_file)
    
    # Load the Excel file
    scraper.load_excel()
    
    # Ask user for sample or full scrape
    print("\nOptions:")
    print("  1. Test with first 5 rows")
    print("  2. Test with first 10 rows")
    print("  3. Process all rows")
    print("  4. Custom range")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        results = scraper.process_all_links(sample_size=5)
    elif choice == '2':
        results = scraper.process_all_links(sample_size=10)
    elif choice == '3':
        results = scraper.process_all_links()
    elif choice == '4':
        start = int(input("Start row (0-based): "))
        end = int(input("End row (exclusive): "))
        results = scraper.process_all_links(start_row=start, end_row=end)
    else:
        print("Invalid choice. Running test with 5 rows...")
        results = scraper.process_all_links(sample_size=5)
    
    # Save results
    output_file = scraper.save_results(results)
    
    print("\n" + "=" * 70)
    print(f"✓ COMPLETED!")
    print(f"  Results saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
