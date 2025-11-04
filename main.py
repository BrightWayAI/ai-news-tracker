#!/usr/bin/env python3
"""
AI News Tracker - Main script
Scrapes AI news from multiple sources and generates reports
"""
import argparse
import configparser
import os
import sys
from datetime import datetime

from database import NewsDatabase
from scrapers import NewsAggregator
from report_generator import ReportGenerator
from email_sender import EmailSender


def load_config(config_file='config.ini'):
    """Load configuration from file"""
    if not os.path.exists(config_file):
        print(f"Error: Config file '{config_file}' not found!")
        print("Please copy config.example.ini to config.ini and fill in your settings")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def scrape_and_store(db: NewsDatabase, aggregator: NewsAggregator) -> int:
    """Scrape all sources and store new articles in database"""
    print("\n=== Starting scraping process ===\n")

    results = aggregator.scrape_all()
    new_articles_count = 0

    for source, articles in results.items():
        print(f"\nProcessing {source}:")
        for article in articles:
            added = db.add_article(
                source=article['source'],
                title=article['title'],
                link=article['link'],
                summary=article.get('summary'),
                published_date=article.get('published_date')
            )
            if added:
                new_articles_count += 1
                print(f"  ✓ Added: {article['title'][:60]}...")
            else:
                print(f"  - Skipped (duplicate): {article['title'][:60]}...")

    print(f"\n=== Scraping complete: {new_articles_count} new articles added ===\n")
    return new_articles_count


def generate_reports(db: NewsDatabase, report_gen: ReportGenerator, days: int = 7):
    """Generate markdown and HTML reports"""
    print(f"\n=== Generating reports for last {days} days ===\n")

    articles = db.get_recent_articles(days=days)
    print(f"Found {len(articles)} articles from the last {days} days")

    if not articles:
        print("No articles to report")
        return None, None

    # Generate markdown report
    date_str = datetime.now().strftime('%Y-%m-%d')
    markdown_path = report_gen.save_markdown_report(articles)
    print(f"✓ Markdown report saved: {markdown_path}")

    # Generate HTML for email
    html_content = report_gen.generate_email_html(articles)
    print(f"✓ HTML email content generated")

    return markdown_path, html_content


def send_email_digest(config: configparser.ConfigParser, html_content: str):
    """Send email digest"""
    print("\n=== Sending email digest ===\n")

    try:
        sender = EmailSender(
            smtp_server=config.get('email', 'smtp_server'),
            smtp_port=config.getint('email', 'smtp_port'),
            sender_email=config.get('email', 'sender_email'),
            sender_password=config.get('email', 'sender_password')
        )

        recipient = config.get('email', 'recipient_email')
        date_str = datetime.now().strftime('%B %d, %Y')

        success = sender.send_digest(recipient, html_content, date_str)

        if success:
            print("✓ Email sent successfully")
        else:
            print("✗ Failed to send email")

        return success
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False


def show_stats(db: NewsDatabase):
    """Display database statistics"""
    stats = db.get_stats()
    print("\n=== Database Statistics ===\n")
    print(f"Total articles: {stats['total_articles']}")
    print("\nArticles by source:")
    for source, count in sorted(stats['by_source'].items()):
        print(f"  {source}: {count}")
    print()


def main():
    parser = argparse.ArgumentParser(description='AI News Tracker')
    parser.add_argument('--config', default='config.ini', help='Config file path')
    parser.add_argument('--scrape', action='store_true', help='Scrape news sources')
    parser.add_argument('--report', action='store_true', help='Generate reports')
    parser.add_argument('--email', action='store_true', help='Send email digest')
    parser.add_argument('--stats', action='store_true', help='Show database stats')
    parser.add_argument('--days', type=int, default=7, help='Number of days for reports (default: 7)')
    parser.add_argument('--all', action='store_true', help='Scrape, generate report, and send email')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Initialize components
    db_path = config.get('storage', 'database', fallback='ai_news.db')
    reports_dir = config.get('storage', 'reports_dir', fallback='reports')
    user_agent = config.get('scraper', 'user_agent',
                           fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    db = NewsDatabase(db_path)
    aggregator = NewsAggregator(user_agent)
    report_gen = ReportGenerator(reports_dir)

    # Execute based on arguments
    if args.stats:
        show_stats(db)

    if args.all or args.scrape:
        scrape_and_store(db, aggregator)

    if args.all or args.report:
        markdown_path, html_content = generate_reports(db, report_gen, args.days)

        if args.all or args.email:
            if html_content:
                send_email_digest(config, html_content)
            else:
                print("No content to email")

    if not any([args.scrape, args.report, args.email, args.stats, args.all]):
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --all              # Scrape, generate report, and send email")
        print("  python main.py --scrape           # Only scrape news sources")
        print("  python main.py --report           # Only generate reports")
        print("  python main.py --stats            # Show database statistics")


if __name__ == '__main__':
    main()
