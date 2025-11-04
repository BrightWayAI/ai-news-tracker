#!/usr/bin/env python3
"""
Test script to verify setup before running the main scraper
"""
import sys
import os
import configparser


def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import requests
        import bs4
        import feedparser
        import dateutil
        import lxml
        print("✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def test_config():
    """Test that config file exists and is valid"""
    print("\nTesting configuration...")

    if not os.path.exists('config.ini'):
        print("✗ config.ini not found")
        print("  Run: cp config.example.ini config.ini")
        print("  Then edit config.ini with your settings")
        return False

    config = configparser.ConfigParser()
    config.read('config.ini')

    # Check required sections
    required = {
        'email': ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_email'],
        'scraper': ['user_agent'],
        'storage': ['database', 'reports_dir']
    }

    all_good = True
    for section, keys in required.items():
        if not config.has_section(section):
            print(f"✗ Missing section: [{section}]")
            all_good = False
            continue

        for key in keys:
            if not config.has_option(section, key):
                print(f"✗ Missing option: {key} in [{section}]")
                all_good = False
            elif not config.get(section, key).strip():
                print(f"✗ Empty value: {key} in [{section}]")
                all_good = False

    if all_good:
        print("✓ Configuration file is valid")

    return all_good


def test_email_config():
    """Test email configuration (without sending)"""
    print("\nTesting email settings...")

    config = configparser.ConfigParser()
    config.read('config.ini')

    if not config.has_section('email'):
        print("✗ Email section missing")
        return False

    smtp_server = config.get('email', 'smtp_server', fallback='')
    sender_email = config.get('email', 'sender_email', fallback='')
    sender_password = config.get('email', 'sender_password', fallback='')

    if 'your-email' in sender_email or 'your-app-password' in sender_password:
        print("✗ Email settings not configured")
        print("  Edit config.ini and add your email settings")
        return False

    print("✓ Email settings appear to be configured")
    print(f"  Server: {smtp_server}")
    print(f"  From: {sender_email}")
    return True


def test_database():
    """Test database creation"""
    print("\nTesting database...")

    try:
        from database import NewsDatabase
        db = NewsDatabase('test.db')

        # Try to add a test article
        success = db.add_article(
            source='Test',
            title='Test Article',
            link='https://example.com/test',
            summary='This is a test',
            published_date='2024-01-01'
        )

        if success:
            print("✓ Database working correctly")

        # Clean up
        os.remove('test.db')
        return True

    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_scraper():
    """Test that scraper can be imported"""
    print("\nTesting scraper...")

    try:
        from scrapers import NewsAggregator
        print("✓ Scraper module loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Scraper error: {e}")
        return False


def main():
    print("=== AI News Tracker Setup Test ===\n")

    tests = [
        test_imports(),
        test_config(),
        test_email_config(),
        test_database(),
        test_scraper(),
    ]

    print("\n" + "="*40)

    if all(tests):
        print("✓ All tests passed! You're ready to run the tracker.")
        print("\nNext steps:")
        print("  1. Test locally: python main.py --scrape")
        print("  2. View stats: python main.py --stats")
        print("  3. Generate report: python main.py --report")
        print("  4. Run full cycle: python main.py --all")
        print("\nFor GitHub Actions setup, see README.md")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
