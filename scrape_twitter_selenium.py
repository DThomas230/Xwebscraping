"""
Enhanced Twitter/X Scraper using Selenium
This version uses browser automation for better success rate
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
from datetime import datetime


class SeleniumTwitterScraper:
    def __init__(self, excel_file='Post Tracker.xlsx', headless=False):
        self.excel_file = excel_file
        self.df = None
        self.driver = None
        self.headless = headless
        self.is_csv = excel_file.lower().endswith('.csv')
        
    def setup_driver(self):
        """Setup Selenium WebDriver with Chrome"""
        print("Setting up Chrome WebDriver...")
        
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✓ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"✗ Error setting up Chrome WebDriver: {e}")
            print("\nPlease ensure:")
            print("  1. Chrome browser is installed")
            print("  2. ChromeDriver is installed (pip install webdriver-manager)")
            return False
    
    def load_excel(self):
        """Load the Excel or CSV file"""
        print(f"\nLoading {'CSV' if self.is_csv else 'Excel'} file...")
        
        if self.is_csv:
            # Read CSV file
            self.df = pd.read_csv(self.excel_file)
        else:
            # Read Excel file
            self.df = pd.read_excel(self.excel_file)
        
        # Rename first column to Post_URL if it contains links
        first_col = self.df.columns[0]
        if first_col != 'Post_URL' and ('link' in first_col.lower() or 'url' in first_col.lower() or 'http' in str(self.df.iloc[0, 0]).lower()):
            print(f"  Renaming column '{first_col}' to 'Post_URL'")
            columns = ['Post_URL'] + list(self.df.columns[1:])
            self.df.columns = columns
        
        print(f"✓ Loaded {len(self.df)} rows")
        print(f"✓ First column: {self.df.columns[0]}")
        return self.df
    
    def parse_count(self, text):
        """Parse count text like '1.2K' or '5M' to numeric value"""
        if not text:
            return None
        
        # Remove any whitespace and convert to uppercase
        text = str(text).strip().upper().replace(',', '').replace(' ', '')
        
        try:
            # Handle K (thousands)
            if 'K' in text:
                num = float(text.replace('K', ''))
                return int(num * 1000)
            # Handle M (millions)
            elif 'M' in text:
                num = float(text.replace('M', ''))
                return int(num * 1000000)
            # Handle B (billions)
            elif 'B' in text:
                num = float(text.replace('B', ''))
                return int(num * 1000000000)
            # Plain number
            else:
                return int(float(text))
        except ValueError as e:
            print(f"    [DEBUG] Error parsing count '{text}': {e}")
            return None
    
    def extract_user_profile_info(self, username):
        """Extract user profile information"""
        if not username:
            return None
        
        profile_data = {
            'followers': None,
            'account_created': None,
            'account_name': None
        }
        
        try:
            profile_url = f"https://x.com/{username}"
            print(f"      Visiting profile: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for profile to load
            
            # Extract account name (display name)
            try:
                name_selectors = [
                    "//div[@data-testid='UserName']//span[contains(@class, 'css-1jxf684')]",
                    "//div[@data-testid='UserName']//span",
                    "//div[contains(@class, 'css-175oi2r')]//span[contains(@class, 'css-1jxf684')]"
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = self.driver.find_element(By.XPATH, selector)
                        name_text = name_element.text
                        if name_text and name_text != f"@{username}":
                            profile_data['account_name'] = name_text
                            print(f"        ✓ Account name: {profile_data['account_name']}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"        ⚠ Could not extract account name: {e}")
            
            # Extract follower count
            try:
                follower_selectors = [
                    "//a[contains(@href, '/verified_followers')]//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']/span",
                    "//a[contains(@href, '/verified_followers')]//span[contains(@class, 'css-1jxf684')]",
                    "//a[contains(@href, '/followers')]//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']/span",
                    "//span[contains(text(), 'Followers')]/preceding-sibling::span"
                ]
                
                for selector in follower_selectors:
                    try:
                        follower_element = self.driver.find_element(By.XPATH, selector)
                        follower_text = follower_element.text.strip()
                        # Convert follower count (handles K, M, etc.)
                        profile_data['followers'] = self.parse_count(follower_text)
                        print(f"        ✓ Followers: {profile_data['followers']} ({follower_text})")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"        ⚠ Could not extract followers: {e}")
            
            # Extract account creation date (joined date)
            try:
                join_selectors = [
                    "//span[contains(text(), 'Joined')]",
                    "//div[contains(@class, 'css-175oi2r')]//span[contains(text(), 'Joined')]"
                ]
                
                for selector in join_selectors:
                    try:
                        join_element = self.driver.find_element(By.XPATH, selector)
                        join_text = join_element.text
                        # Extract date from "Joined Month Year" format
                        if 'Joined' in join_text:
                            profile_data['account_created'] = join_text.replace('Joined ', '').strip()
                            print(f"        ✓ Account created: {profile_data['account_created']}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"        ⚠ Could not extract join date: {e}")
            
            return profile_data
            
        except Exception as e:
            print(f"      ✗ Error accessing profile: {e}")
            return profile_data
    
    def extract_tweet_info(self, url):
        """Extract tweet information using Selenium"""
        if pd.isna(url) or not isinstance(url, str) or 'http' not in url:
            return None
        
        data = {
            'url': url,
            'username': None,
            'display_name': None,
            'text': None,
            'likes': None,
            'retweets': None,
            'replies': None,
            'views': None,
            'bookmarks': None,
            'timestamp': None,
            'language': None,
            'has_media': False,
            'has_video': 0,  # Changed to 0/1 format for video detection
            'has_image': False,
            'is_retweet': False,
            'followers': None,
            'account_created': None,
            'account_name': None,
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            print(f"    Loading page...")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(3)  # Initial wait for dynamic content
            
            # Try to extract username from URL
            username_match = re.search(r'x\.com/([^/]+)/', url)
            if username_match:
                data['username'] = username_match.group(1)
            
            # Extract tweet text
            try:
                # Twitter uses data-testid for elements
                tweet_text_selectors = [
                    "//div[@data-testid='tweetText']",
                    "//div[@lang]//span[contains(@class, 'css-1qaijid')]",
                    "//article//div[@lang]"
                ]
                
                for selector in tweet_text_selectors:
                    try:
                        tweet_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        data['text'] = tweet_element.text
                        print(f"    ✓ Extracted text: {data['text'][:50]}...")
                        break
                    except:
                        continue
                        
            except Exception as e:
                print(f"    ⚠ Could not extract text: {e}")
            
            # Extract engagement metrics (likes, retweets, replies, views)
            try:
                # Look for aria-label attributes that contain engagement metrics
                engagement_elements = self.driver.find_elements(By.XPATH, "//a[@role='link'][@aria-label]")
                
                for element in engagement_elements:
                    aria_label = element.get_attribute('aria-label')
                    if aria_label:
                        # Parse likes - handles both plain numbers and abbreviated (1.2K, 5M)
                        if 'like' in aria_label.lower():
                            match = re.search(r'([\d,\.]+[KMB]?)', aria_label)
                            if match:
                                data['likes'] = self.parse_count(match.group(1))
                        
                        # Parse retweets
                        if 'retweet' in aria_label.lower() or 'repost' in aria_label.lower():
                            match = re.search(r'([\d,\.]+[KMB]?)', aria_label)
                            if match:
                                data['retweets'] = self.parse_count(match.group(1))
                        
                        # Parse replies
                        if 'repl' in aria_label.lower():
                            match = re.search(r'([\d,\.]+[KMB]?)', aria_label)
                            if match:
                                data['replies'] = self.parse_count(match.group(1))
                        
                        # Parse bookmarks
                        if 'bookmark' in aria_label.lower():
                            match = re.search(r'([\d,\.]+[KMB]?)', aria_label)
                            if match:
                                data['bookmarks'] = self.parse_count(match.group(1))
                        
                        # Parse views
                        if 'view' in aria_label.lower():
                            match = re.search(r'([\d,\.]+[KMB]?)', aria_label)
                            if match:
                                data['views'] = self.parse_count(match.group(1))
                
                # Alternative: Try to find engagement by data-testid and look at buttons/text
                try:
                    like_button = self.driver.find_element(By.XPATH, "//button[@data-testid='like']")
                    like_text = like_button.get_attribute('aria-label')
                    if like_text:
                        match = re.search(r'([\d,\.]+[KMB]?)', like_text)
                        if match and not data['likes']:
                            data['likes'] = self.parse_count(match.group(1))
                except:
                    pass
                
                try:
                    retweet_button = self.driver.find_element(By.XPATH, "//button[@data-testid='retweet']")
                    retweet_text = retweet_button.get_attribute('aria-label')
                    if retweet_text:
                        match = re.search(r'([\d,\.]+[KMB]?)', retweet_text)
                        if match and not data['retweets']:
                            data['retweets'] = self.parse_count(match.group(1))
                except:
                    pass
                
                try:
                    reply_button = self.driver.find_element(By.XPATH, "//button[@data-testid='reply']")
                    reply_text = reply_button.get_attribute('aria-label')
                    if reply_text:
                        match = re.search(r'([\d,\.]+[KMB]?)', reply_text)
                        if match and not data['replies']:
                            data['replies'] = self.parse_count(match.group(1))
                except:
                    pass
                
                # Extract bookmarks with improved selectors
                try:
                    bookmark_button = self.driver.find_element(By.XPATH, "//button[@data-testid='bookmark']")
                    bookmark_text = bookmark_button.get_attribute('aria-label')
                    if bookmark_text:
                        match = re.search(r'([\d,\.]+[KMB]?)', bookmark_text)
                        if match and not data['bookmarks']:
                            data['bookmarks'] = self.parse_count(match.group(1))
                except:
                    pass
                
                # Extract views - Twitter shows views in the engagement bar
                # Method 1: Look for any link with 'analytics' that shows view count
                if not data['views']:
                    try:
                        # Find the analytics link (usually at bottom of tweet with views)
                        analytics_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/analytics')]")
                        print(f"    [DEBUG] Found {len(analytics_elements)} analytics elements")
                        
                        for element in analytics_elements:
                            # Get all text within this element and its children
                            full_text = element.text.strip()
                            print(f"    [DEBUG] Analytics element full text: '{full_text}'")
                            
                            # Try to get inner span specifically
                            try:
                                inner_spans = element.find_elements(By.XPATH, ".//span")
                                for span in inner_spans:
                                    span_text = span.text.strip()
                                    if span_text:
                                        print(f"    [DEBUG] Analytics span text: '{span_text}'")
                                        # Match patterns like "4.3M" or "4400"
                                        if re.match(r'^[\d,\.]+[KMB]?$', span_text):
                                            potential_views = self.parse_count(span_text)
                                            print(f"    [DEBUG] Parsed views from analytics span: {potential_views}")
                                            if potential_views and potential_views > 0:
                                                data['views'] = potential_views
                                                break
                            except:
                                pass
                            
                            # Also try the full text if spans didn't work
                            if not data['views'] and full_text:
                                # Extract just the number part (before or after "Views")
                                match = re.search(r'([\d,\.]+[KMB]?)', full_text)
                                if match:
                                    potential_views = self.parse_count(match.group(1))
                                    print(f"    [DEBUG] Parsed views from analytics full text: {potential_views}")
                                    if potential_views and potential_views > 0:
                                        data['views'] = potential_views
                            
                            if data['views']:
                                break
                    except Exception as e:
                        print(f"    [DEBUG] Analytics method error: {e}")
                
                # Method 2: Look for time element and then find views nearby
                if not data['views']:
                    try:
                        # Views are usually displayed near the timestamp
                        time_element = self.driver.find_element(By.XPATH, "//article//time")
                        # Navigate to parent and look for views
                        parent = time_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'css-175oi2r')]")
                        view_texts = parent.find_elements(By.XPATH, ".//span[contains(text(), 'Views') or preceding-sibling::span]")
                        
                        print(f"    [DEBUG] Found {len(view_texts)} potential view elements near timestamp")
                        for elem in view_texts:
                            text = elem.text.strip()
                            print(f"    [DEBUG] Near timestamp text: '{text}'")
                            if text and re.match(r'^[\d,\.]+[KMB]?$', text):
                                potential_views = self.parse_count(text)
                                if potential_views and potential_views > 0:
                                    data['views'] = potential_views
                                    print(f"    [DEBUG] Parsed views from timestamp area: {potential_views}")
                                    break
                    except Exception as e:
                        print(f"    [DEBUG] Timestamp method error: {e}")
                
                # Method 3: Look for "Views" text and extract number before it
                if not data['views']:
                    try:
                        # Search for elements containing "Views"
                        view_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Views')]")
                        print(f"    [DEBUG] Found {len(view_elements)} elements with 'Views' text")
                        
                        for element in view_elements:
                            text = element.text.strip()
                            print(f"    [DEBUG] Views element text: '{text}'")
                            # Match "4.3M Views" or "4,400 Views"
                            match = re.search(r'([\d,\.]+[KMB]?)\s*Views?', text, re.IGNORECASE)
                            if match:
                                data['views'] = self.parse_count(match.group(1))
                                print(f"    [DEBUG] Extracted views from 'Views' text: {data['views']}")
                                break
                            
                            # Also check parent element
                            try:
                                parent_text = element.find_element(By.XPATH, "./..").text.strip()
                                if parent_text != text:
                                    print(f"    [DEBUG] Parent element text: '{parent_text}'")
                                    match = re.search(r'([\d,\.]+[KMB]?)\s*Views?', parent_text, re.IGNORECASE)
                                    if match:
                                        data['views'] = self.parse_count(match.group(1))
                                        print(f"    [DEBUG] Extracted views from parent: {data['views']}")
                                        break
                            except:
                                pass
                    except Exception as e:
                        print(f"    [DEBUG] 'Views' text method error: {e}")
                
                # Method 4: Scan all engagement area spans for the largest number (likely views)
                if not data['views']:
                    try:
                        # Get all numbers from the engagement section
                        article = self.driver.find_element(By.XPATH, "//article")
                        all_spans = article.find_elements(By.XPATH, ".//span")
                        
                        candidates = []
                        for span in all_spans:
                            text = span.text.strip()
                            # Only consider standalone numbers (not part of longer text)
                            if text and re.match(r'^[\d,\.]+[KMB]?$', text):
                                num = self.parse_count(text)
                                if num and num > 0:
                                    candidates.append((text, num))
                        
                        print(f"    [DEBUG] Found {len(candidates)} numeric candidates: {candidates}")
                        
                        # Filter out known metrics and find views (usually the largest remaining number)
                        for text, num in sorted(candidates, key=lambda x: x[1], reverse=True):
                            if (num != data['likes'] and 
                                num != data['retweets'] and 
                                num != data['replies'] and 
                                num != data['bookmarks']):
                                data['views'] = num
                                print(f"    [DEBUG] Selected views (largest unmatched): {num}")
                                break
                    except Exception as e:
                        print(f"    [DEBUG] Engagement scanning method error: {e}")
                
                print(f"    ✓ Engagement - Likes: {data['likes']}, Retweets: {data['retweets']}, Replies: {data['replies']}, Views: {data['views']}, Bookmarks: {data['bookmarks']}")
                
            except Exception as e:
                print(f"    ⚠ Could not extract engagement metrics: {e}")
            
            # Check for media and specifically detect videos
            try:
                images = self.driver.find_elements(By.XPATH, "//img[@alt='Image']")
                if images:
                    data['has_image'] = True
                    data['has_media'] = True
                
                # Video detection - set to 1 if video exists, 0 otherwise
                video_selectors = [
                    "//video",
                    "//div[@data-testid='videoPlayer']",
                    "//div[@data-testid='playButton']",
                    "//div[contains(@aria-label, 'video')]"
                ]
                
                has_video = False
                for selector in video_selectors:
                    try:
                        video_elements = self.driver.find_elements(By.XPATH, selector)
                        if video_elements:
                            has_video = True
                            break
                    except:
                        continue
                
                data['has_video'] = 1 if has_video else 0
                if has_video:
                    data['has_media'] = True
                    
                print(f"    ✓ Media - Images: {data['has_image']}, Video: {data['has_video']}")
            except:
                pass
            
            # Extract timestamp
            try:
                time_elements = self.driver.find_elements(By.TAG_NAME, 'time')
                if time_elements:
                    data['timestamp'] = time_elements[0].get_attribute('datetime')
                    print(f"    ✓ Timestamp: {data['timestamp']}")
            except:
                pass
            
            # Extract user profile information
            if data['username']:
                print(f"    Extracting profile information for @{data['username']}...")
                profile_info = self.extract_user_profile_info(data['username'])
                if profile_info:
                    data['followers'] = profile_info.get('followers')
                    data['account_created'] = profile_info.get('account_created')
                    data['account_name'] = profile_info.get('account_name')
                    # Use account_name as display_name
                    if profile_info.get('account_name'):
                        data['display_name'] = profile_info.get('account_name')
            
            data['status'] = 'success'
            print(f"    ✓ Successfully scraped tweet")
            
        except TimeoutException:
            data['status'] = 'timeout'
            print(f"    ✗ Timeout loading page")
        except Exception as e:
            data['status'] = f'error: {str(e)[:50]}'
            print(f"    ✗ Error: {str(e)[:100]}")
        
        return data
    
    def process_links(self, start_row=0, end_row=None, sample_size=None):
        """Process Twitter/X links"""
        if self.df is None:
            self.load_excel()
        
        if not self.setup_driver():
            return None
        
        # Determine which rows to process
        if sample_size:
            end_row = min(start_row + sample_size, len(self.df))
        elif end_row is None:
            end_row = len(self.df)
        
        print(f"\nProcessing rows {start_row} to {end_row-1} ({end_row - start_row} rows)")
        print("=" * 70)
        
        results = []
        
        try:
            for idx in range(start_row, end_row):
                url = self.df.iloc[idx]['Post_URL']
                
                print(f"\n[{idx + 1}/{end_row}] Processing: {url}")
                
                if pd.isna(url) or not isinstance(url, str) or 'http' not in url:
                    print("  ⊘ Skipping (no valid URL)")
                    results.append(None)
                    continue
                
                data = self.extract_tweet_info(url)
                results.append(data)
                
                # Delay between requests
                time.sleep(2)
        
        finally:
            # Close the browser
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()
        
        return results
    
    def save_results(self, results, output_file=None):
        """Save results to Excel or CSV"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_ext = '.csv' if self.is_csv else '.xlsx'
            output_file = f'Post Tracker_scraped_{timestamp}{file_ext}'
        
        print(f"\nSaving results to: {output_file}")
        
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        
        if valid_results:
            # Create DataFrame from results
            results_df = pd.DataFrame(valid_results)
            
            # Define column mappings for better readability
            column_mappings = {
                'username': 'Username',
                'display_name': 'Display Name',
                'account_name': 'Account Name',
                'text': 'Tweet Text',
                'likes': 'Likes',
                'retweets': 'Retweets',
                'replies': 'Replies',
                'views': 'Views',
                'bookmarks': 'Bookmarks',
                'timestamp': 'Timestamp',
                'has_video': 'Has Video',
                'has_image': 'Has Image',
                'has_media': 'Has Media',
                'followers': 'Followers',
                'account_created': 'Account Created',
                'is_retweet': 'Is Retweet',
                'language': 'Language',
                'scraped_at': 'Scraped At',
                'status': 'Status'
            }
            
            # Initialize new columns in the original DataFrame
            for original_col, new_col in column_mappings.items():
                if original_col in results_df.columns:
                    self.df[new_col] = None
            
            # Fill in the scraped data row by row
            for idx, result in enumerate(valid_results):
                if result:
                    for original_col, new_col in column_mappings.items():
                        if original_col in result and new_col in self.df.columns:
                            self.df.at[idx, new_col] = result[original_col]
        
        # Save to CSV or Excel
        if self.is_csv:
            self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            self.df.to_excel(output_file, index=False)
        print(f"✓ Saved to: {output_file}")
        
        # Print summary
        if valid_results:
            success_count = sum(1 for r in valid_results if r.get('status') == 'success')
            print(f"\nSummary:")
            print(f"  Total processed: {len(results)}")
            print(f"  Successful: {success_count}")
            print(f"  Failed: {len(valid_results) - success_count}")
            
            # Summary of new data collected
            videos_count = sum(1 for r in valid_results if r.get('has_video') == 1)
            views_count = sum(1 for r in valid_results if r.get('views') is not None)
            profiles_count = sum(1 for r in valid_results if r.get('followers') is not None)
            
            print(f"\nData Collected:")
            print(f"  Posts with videos: {videos_count}")
            print(f"  Posts with view counts: {views_count}")
            print(f"  Profiles scraped: {profiles_count}")
        
        return output_file


def main():
    """Main execution"""
    print("=" * 70)
    print("SELENIUM TWITTER/X SCRAPER")
    print("=" * 70)
    print("\nThis script uses browser automation to scrape Twitter/X data.")
    print("\nNOTE: You may need to log in to Twitter/X manually when the browser opens")
    print("      if the tweets are from private accounts or require authentication.")
    print("\n" + "=" * 70)
    
    # Initialize scraper
    scraper = SeleniumTwitterScraper('Post Tracker.xlsx', headless=False)
    
    # Load Excel
    scraper.load_excel()
    
    # Choose how many to process
    print("\nOptions:")
    print("  1. Test with first 3 rows")
    print("  2. Test with first 10 rows")
    print("  3. Process all rows")
    print("  4. Custom range")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        results = scraper.process_links(sample_size=3)
    elif choice == '2':
        results = scraper.process_links(sample_size=10)
    elif choice == '3':
        results = scraper.process_links()
    elif choice == '4':
        start = int(input("Start row (0-based): "))
        end = int(input("End row (exclusive): "))
        results = scraper.process_links(start_row=start, end_row=end)
    else:
        print("Invalid choice. Running test with 3 rows...")
        results = scraper.process_links(sample_size=3)
    
    # Save results
    if results:
        scraper.save_results(results)
    
    print("\n" + "=" * 70)
    print("✓ COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
