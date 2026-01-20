"""
Mixpanel Dashboard Scraper using Playwright
Extracts periodic data from public dashboards
"""

import asyncio
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

class MixpanelScraper:
    """Scraper for Mixpanel public dashboards"""

    def __init__(self, dashboard_url: str):
        self.dashboard_url = dashboard_url
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_data(self) -> Dict[str, List[Dict]]:
        """
        Scrape data from the dashboard
        """
        try:
            page = await self.context.new_page()
            
            # Store captured API responses in a list (Mixpanel calls the same endpoint multiple times)
            captured_responses = []
            
            # Intercept network requests to capture Mixpanel API data
            async def handle_response(response):
                try:
                    url = response.url
                    if 'api' in url and response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            try:
                                json_data = await response.json()
                                captured_responses.append({
                                    'url': url,
                                    'data': json_data
                                })
                            except:
                                pass
                except:
                    pass
            
            page.on('response', handle_response)
            
            # Navigate to dashboard
            await page.goto(self.dashboard_url, wait_until='networkidle', timeout=90000)
            
            # Wait for dashboard cards to be present
            await page.wait_for_selector('mp-dash-card', timeout=60000)
            
            # Wait for content to render
            await page.wait_for_timeout(10000)
            
            # Extract data using the network interception approach
            # We don't need DOM parsing anymore as API capture is exact
            
            # Wait for content to render to ensure all API calls are made
            await page.wait_for_timeout(10000)
            
            await page.close()
            
            # Process captured API responses
            results = {}
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            from datetime import datetime as dt_class
            
            def format_mixpanel_date(date_str):
                # Handle ISO8601 like "2026-01-13T00:00:00-05:00"
                try:
                    # Strip timezone for simple parsing or use fromisoformat if available
                    clean_date = date_str.split('T')[0]
                    parsed = dt_class.strptime(clean_date, '%Y-%m-%d')
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    return f"{months[parsed.month - 1]} {parsed.day}", clean_date
                except:
                    return date_str, date_str

            for entry in captured_responses:
                url = entry['url']
                api_data = entry['data']
                
                if 'dashboard-cards' in url and isinstance(api_data, dict):
                    # Mixpanel dashboard-cards results are often nested in results.series
                    inner_results = api_data.get('results', {})
                    series_map = inner_results.get('series', {})
                    
                    if not series_map:
                        continue
                        
                    for series_name, data_map in series_map.items():
                        # Determine if this is a series we care about
                        target_title = None
                        if 'apk install' in series_name.lower() or 'uniques of install' in series_name.lower():
                            target_title = 'Installs'
                        elif 'trial_started' in series_name.lower():
                            target_title = 'Daily Trial Started'
                        
                        if not target_title:
                            continue
                            
                        # Extract and sort data points by date
                        data_points = []
                        # data_map is { "ISO_DATE": value }
                        sorted_dates = sorted(data_map.keys())
                        
                        for d_str in sorted_dates:
                            val = data_map[d_str]
                            display_date, iso_date = format_mixpanel_date(d_str)
                            
                            # Exclude today
                            if iso_date == today_str:
                                continue
                                
                            data_points.append({
                                'x': display_date,
                                'y': int(val) if val is not None else 0
                            })
                        
                        if data_points:
                            results[target_title] = [{'name': 'Scraped Data', 'data': data_points}]
            
            # Log results found
            if results:
                print(f"Successfully extracted data from Mixpanel API for: {list(results.keys())}")
                return results
            else:
                print("Failed to find relevant chart data in captured API responses.")
                return {}

        except Exception as e:
            print(f"Error scraping Mixpanel: {e}")
            return {}

async def test():
    url = "https://mixpanel.com/p/SJdKzRbuddFHjaHtbUvtrk"
    async with MixpanelScraper(url) as scraper:
        data = await scraper.scrape_data()
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
