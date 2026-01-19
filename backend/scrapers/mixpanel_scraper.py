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
            
            # Navigate to dashboard
            await page.goto(self.dashboard_url, wait_until='networkidle', timeout=90000)
            
            # Wait for dashboard cards to be present
            await page.wait_for_selector('mp-dash-card', timeout=60000)
            
            # Wait for content to render
            await page.wait_for_timeout(10000)
            
            # Extract data from Highcharts global instances or by parsing SVG/DOM
            data = await page.evaluate(r'''() => {
                const results = {};
                
                // Helper to parse dates like "Jan 19", "Dec 20"
                const parseDate = (str) => {
                    const months = {
                        'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
                        'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
                    };
                    const parts = str.trim().split(' ');
                    if (parts.length < 2) return null;
                    const month = months[parts[0]];
                    const day = parseInt(parts[1]);
                    if (month === undefined || isNaN(day)) return null;
                    
                    const date = new Date();
                    const now = new Date();
                    date.setMonth(month);
                    date.setDate(day);
                    date.setHours(0, 0, 0, 0);
                    
                    if (month > now.getMonth()) {
                        date.setFullYear(now.getFullYear() - 1);
                    } else {
                        date.setFullYear(now.getFullYear());
                    }
                    return date;
                };

                const formatDate = (date) => {
                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    return `${months[date.getMonth()]} ${date.getDate()}`;
                };

                const now = new Date();
                const thirtyDaysAgo = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000));
                thirtyDaysAgo.setHours(0, 0, 0, 0);

                // Iterate over dashboard cards
                document.querySelectorAll('mp-dash-card').forEach((card, index) => {
                    const titleEl = card.querySelector('.report-name, .card-title, h2, h3');
                    let rawTitle = titleEl ? titleEl.textContent.trim() : `Chart ${index}`;
                    
                    // Standardize titles
                    let title = rawTitle;
                    if (rawTitle.includes('Installs')) title = 'Installs';
                    else if (rawTitle.includes('Trial Started')) title = 'Daily Trial Started';
                    else return; // Skip other charts (like Conversion Funnel)

                    // Time-series Chart Detection (SVG/Highcharts)
                    const svg = card.querySelector('svg');
                    if (svg) {
                        // Sort labels by x coordinate to ensure left-to-right order
                        const labels = Array.from(svg.querySelectorAll('.highcharts-xaxis-labels text'))
                            .map(el => ({
                                text: el.textContent,
                                x: parseFloat(el.getAttribute('x') || 0),
                                date: parseDate(el.textContent)
                            }))
                            .filter(l => l.date !== null)
                            .sort((a, b) => a.x - b.x);

                        const yLabels = Array.from(svg.querySelectorAll('.highcharts-yaxis-labels text'))
                                    .map(el => parseFloat(el.textContent.replace(/[^\d\.]/g, '')))
                                    .filter(v => !isNaN(v))
                                    .sort((a, b) => a - b);
                        const maxY = yLabels[yLabels.length - 1] || 100;
                        
                        const tempPoints = [];
                        const seriesPath = svg.querySelector('.highcharts-series path');
                        if (seriesPath) {
                            const dAttr = seriesPath.getAttribute('d');
                            const matches = dAttr.match(/[ML] ([\d\.]+) ([\d\.]+)/g);
                            if (matches && labels.length >= 2) {
                                const yAxisHeight = 200; // Heuristic
                                const firstLabel = labels[0];
                                const lastLabel = labels[labels.length - 1];
                                const xSpan = lastLabel.x - firstLabel.x;
                                const timeSpan = lastLabel.date - firstLabel.date;

                                matches.forEach((m) => {
                                    const parts = m.split(' ');
                                    const px = parseFloat(parts[1]);
                                    const py = parseFloat(parts[2]);
                                    const val = Math.round(Math.max(0, (yAxisHeight - py) / yAxisHeight * maxY));
                                    
                                    const timeOffset = ((px - firstLabel.x) / xSpan) * timeSpan;
                                    const pointDate = new Date(firstLabel.date.getTime() + timeOffset);
                                    
                                    if (pointDate >= thirtyDaysAgo) {
                                        tempPoints.push({ 
                                            px: px, // Keep px for sorting
                                            x: formatDate(pointDate), 
                                            y: val 
                                        });
                                    }
                                });
                            }
                        }
                        
                        const sortedPoints = tempPoints
                            .sort((a, b) => a.px - b.px)
                            .map(p => ({ x: p.x, y: p.y }));
                            
                        if (sortedPoints.length > 0) {
                            results[title] = [{ name: 'Scraped Data', data: sortedPoints }];
                        }
                    }
                });
                return results;
            }''')
            
            await page.close()
            return data

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
