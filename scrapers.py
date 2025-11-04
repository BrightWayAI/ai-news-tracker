"""
Web scrapers for AI news sources
"""
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import time
import re


class BaseScraper:
    """Base class for all scrapers"""

    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch a web page with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None

    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to ISO format"""
        if not date_str:
            return None

        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.date().isoformat()
            except ValueError:
                continue

        # Try extracting date with regex
        date_pattern = r'(\w+ \d+, \d{4})'
        match = re.search(date_pattern, date_str)
        if match:
            try:
                dt = datetime.strptime(match.group(1), '%B %d, %Y')
                return dt.date().isoformat()
            except ValueError:
                pass

        return None


class OpenAIScraper(BaseScraper):
    """Scraper for OpenAI news"""

    def scrape(self) -> List[Dict]:
        """Scrape OpenAI news page"""
        url = "https://openai.com/news/"
        html = self.fetch_page(url)

        if not html:
            print("Failed to fetch OpenAI news")
            return []

        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # OpenAI uses article cards - adjust selectors as needed
        # Note: These selectors may need adjustment based on actual HTML structure
        article_cards = soup.find_all('a', href=re.compile(r'/news/'))

        for card in article_cards[:10]:  # Limit to 10 most recent
            try:
                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = card.get('href', '')

                # Make link absolute
                if link.startswith('/'):
                    link = f"https://openai.com{link}"

                # Extract date if available
                date_elem = card.find('time')
                published_date = None
                if date_elem:
                    published_date = self.parse_date(date_elem.get_text(strip=True))

                # Extract summary
                summary_elem = card.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else None

                articles.append({
                    'source': 'OpenAI',
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published_date': published_date
                })
            except Exception as e:
                print(f"Error parsing OpenAI article: {e}")
                continue

        return articles


class AnthropicScraper(BaseScraper):
    """Scraper for Anthropic news"""

    def scrape(self) -> List[Dict]:
        """Scrape Anthropic news page"""
        url = "https://www.anthropic.com/news"
        html = self.fetch_page(url)

        if not html:
            print("Failed to fetch Anthropic news")
            return []

        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # Find article cards
        article_cards = soup.find_all('a', href=re.compile(r'/news/'))

        for card in article_cards[:10]:
            try:
                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = card.get('href', '')

                # Make link absolute
                if link.startswith('/'):
                    link = f"https://www.anthropic.com{link}"

                # Extract date
                published_date = None
                date_text = card.get_text()
                # Look for date patterns like "Sep 29, 2025"
                date_match = re.search(r'([A-Z][a-z]{2} \d{1,2}, \d{4})', date_text)
                if date_match:
                    published_date = self.parse_date(date_match.group(1))

                # Extract summary
                summary = None
                paragraphs = card.find_all('p')
                if paragraphs:
                    summary = paragraphs[0].get_text(strip=True)

                articles.append({
                    'source': 'Anthropic',
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published_date': published_date
                })
            except Exception as e:
                print(f"Error parsing Anthropic article: {e}")
                continue

        return articles


class GoogleGeminiScraper(BaseScraper):
    """Scraper for Google Gemini blog"""

    def scrape(self) -> List[Dict]:
        """Scrape Google Gemini blog"""
        url = "https://blog.google/products/gemini/"
        html = self.fetch_page(url)

        if not html:
            print("Failed to fetch Google Gemini blog")
            return []

        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # Find article cards
        article_cards = soup.find_all('article')

        for card in article_cards[:10]:
            try:
                # Find link
                link_elem = card.find('a', href=True)
                if not link_elem:
                    continue

                link = link_elem.get('href', '')
                if link.startswith('/'):
                    link = f"https://blog.google{link}"

                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    title_elem = link_elem
                title = title_elem.get_text(strip=True)

                # Extract date
                published_date = None
                date_elem = card.find('time')
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    published_date = self.parse_date(date_str)

                # Extract summary
                summary = None
                summary_elem = card.find('p')
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)

                articles.append({
                    'source': 'Google Gemini',
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published_date': published_date
                })
            except Exception as e:
                print(f"Error parsing Google Gemini article: {e}")
                continue

        return articles


class DeepViewScraper(BaseScraper):
    """Scraper for The Deep View (uses RSS)"""

    def scrape(self) -> List[Dict]:
        """Scrape The Deep View RSS feed"""
        feed_url = "https://rss.beehiiv.com/feeds/nswNBn2yqy.xml"

        try:
            feed = feedparser.parse(feed_url)
            articles = []

            for entry in feed.entries[:10]:
                # Extract date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    dt = datetime(*entry.published_parsed[:6])
                    published_date = dt.date().isoformat()

                # Extract summary
                summary = None
                if hasattr(entry, 'summary'):
                    # Clean HTML tags from summary
                    summary_soup = BeautifulSoup(entry.summary, 'lxml')
                    summary = summary_soup.get_text(strip=True)[:500]

                articles.append({
                    'source': 'The Deep View',
                    'title': entry.title,
                    'link': entry.link,
                    'summary': summary,
                    'published_date': published_date
                })

            return articles
        except Exception as e:
            print(f"Error fetching The Deep View RSS: {e}")
            return []


class NVIDIAScraper(BaseScraper):
    """Scraper for NVIDIA news"""

    def scrape(self) -> List[Dict]:
        """Scrape NVIDIA news page"""
        url = "https://nvidianews.nvidia.com/"
        html = self.fetch_page(url)

        if not html:
            print("Failed to fetch NVIDIA news")
            return []

        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # Find article cards
        article_cards = soup.find_all(['article', 'div'], class_=re.compile(r'(article|post|news|item)'))

        for card in article_cards[:10]:
            try:
                # Find link
                link_elem = card.find('a', href=True)
                if not link_elem:
                    continue

                link = link_elem.get('href', '')
                if link.startswith('/'):
                    link = f"https://nvidianews.nvidia.com{link}"

                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    title_elem = link_elem
                title = title_elem.get_text(strip=True)

                # Skip if title is too short (likely not an article)
                if len(title) < 10:
                    continue

                # Extract date
                published_date = None
                # Look for date patterns
                date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', card.get_text())
                if date_match:
                    published_date = self.parse_date(date_match.group(1))

                # Extract summary
                summary = None
                paragraphs = card.find_all('p')
                if paragraphs:
                    summary = paragraphs[0].get_text(strip=True)

                articles.append({
                    'source': 'NVIDIA',
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published_date': published_date
                })
            except Exception as e:
                print(f"Error parsing NVIDIA article: {e}")
                continue

        return articles


class EveryToScraper(BaseScraper):
    """Scraper for Every.to newsletter"""

    def scrape(self) -> List[Dict]:
        """Scrape Every.to"""
        url = "https://every.to/"
        html = self.fetch_page(url)

        if not html:
            print("Failed to fetch Every.to")
            return []

        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # Find article cards
        article_cards = soup.find_all('a', href=re.compile(r'/'))

        seen_links = set()

        for card in article_cards:
            try:
                link = card.get('href', '')

                # Skip if already seen
                if link in seen_links:
                    continue

                # Make link absolute
                if link.startswith('/'):
                    link = f"https://every.to{link}"

                # Must be an article link
                if not any(x in link for x in ['every.to/p/', 'every.to/c/', 'every.to/chain-of-thought']):
                    continue

                seen_links.add(link)

                # Extract title
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    # Try getting text directly
                    title_text = card.get_text(strip=True)
                    if len(title_text) > 200 or len(title_text) < 10:
                        continue
                    title = title_text
                else:
                    title = title_elem.get_text(strip=True)

                # Extract date - look for date patterns
                published_date = None
                date_match = re.search(r'([A-Z][a-z]{2} \d{1,2}, \d{4})', card.get_text())
                if date_match:
                    published_date = self.parse_date(date_match.group(1))

                # Extract summary
                summary = None
                paragraphs = card.find_all('p')
                if paragraphs:
                    summary = paragraphs[0].get_text(strip=True)

                articles.append({
                    'source': 'Every.to',
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published_date': published_date
                })

                if len(articles) >= 10:
                    break
            except Exception as e:
                print(f"Error parsing Every.to article: {e}")
                continue

        return articles


class NewsAggregator:
    """Aggregates news from all sources"""

    def __init__(self, user_agent: str):
        self.scrapers = [
            OpenAIScraper(user_agent),
            AnthropicScraper(user_agent),
            GoogleGeminiScraper(user_agent),
            DeepViewScraper(user_agent),
            NVIDIAScraper(user_agent),
            EveryToScraper(user_agent),
        ]

    def scrape_all(self) -> Dict[str, List[Dict]]:
        """Scrape all sources and return results grouped by source"""
        results = {}

        for scraper in self.scrapers:
            source_name = scraper.__class__.__name__.replace('Scraper', '')
            print(f"Scraping {source_name}...")

            try:
                articles = scraper.scrape()
                results[source_name] = articles
                print(f"  Found {len(articles)} articles")
                time.sleep(1)  # Be polite to servers
            except Exception as e:
                print(f"  Error scraping {source_name}: {e}")
                results[source_name] = []

        return results
