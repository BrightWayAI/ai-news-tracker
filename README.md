# AI News Tracker

Automated system to track and digest the latest developments in AI from major companies and newsletters.

## Features

- **Multi-Source Scraping**: Automatically scrapes news from:
  - OpenAI
  - Anthropic (Claude)
  - Google Gemini
  - NVIDIA
  - The Deep View
  - Every.to

- **Smart Storage**: SQLite database tracks articles and prevents duplicates
- **Markdown Reports**: Beautiful markdown reports saved locally
- **Email Digests**: HTML email summaries sent weekly
- **GitHub Actions**: Automated weekly execution (free!)
- **Configurable**: Easy configuration via INI file

## Quick Start

### 1. Clone or Download

```bash
cd ai-news-tracker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

Copy the example config and edit with your settings:

```bash
cp config.example.ini config.ini
```

Edit `config.ini` and add your email settings:

```ini
[email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = your-email@gmail.com
sender_password = your-app-password
recipient_email = your-email@gmail.com
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use the app password (not your regular password) in the config

### 4. Run Locally

Scrape news and send digest:
```bash
python main.py --all
```

Just scrape (no email):
```bash
python main.py --scrape
```

Generate report from existing data:
```bash
python main.py --report
```

View statistics:
```bash
python main.py --stats
```

## GitHub Actions Setup (Automated Weekly Digests)

### Why GitHub Actions?

- **Free**: Unlimited minutes for public repos, 2,000 min/month for private
- **Automated**: Runs every Monday at 9 AM UTC
- **No Server Needed**: GitHub handles everything
- **Data Persistence**: Database and reports stored in the repo

### Setup Steps

1. **Create a GitHub repository**
   ```bash
   cd ai-news-tracker
   git init
   git add .
   git commit -m "Initial commit: AI News Tracker"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-news-tracker.git
   git push -u origin main
   ```

2. **Add GitHub Secrets**

   Go to your repo → Settings → Secrets and variables → Actions → New repository secret

   Add these secrets:
   - `SMTP_SERVER` (e.g., `smtp.gmail.com`)
   - `SMTP_PORT` (e.g., `587`)
   - `SENDER_EMAIL` (your email)
   - `SENDER_PASSWORD` (your app password)
   - `RECIPIENT_EMAIL` (where to send digest)

3. **Enable GitHub Actions**

   Go to Actions tab → Enable workflows

4. **Test the workflow**

   Actions tab → "Weekly AI News Digest" → "Run workflow"

### How It Works

1. Every Monday at 9 AM UTC, GitHub Actions:
   - Checks out your repo
   - Installs Python dependencies
   - Creates config from secrets
   - Runs the scraper
   - Generates reports
   - Sends email digest
   - Commits database and reports back to repo

2. You receive an email with the week's AI news

3. Reports are also saved in the `reports/` directory in your repo

## Project Structure

```
ai-news-tracker/
├── .github/
│   └── workflows/
│       └── weekly-digest.yml    # GitHub Actions workflow
├── reports/                     # Generated markdown reports
├── config.example.ini           # Configuration template
├── config.ini                   # Your config (gitignored)
├── database.py                  # Database management
├── scrapers.py                  # Web scrapers for each source
├── report_generator.py          # Markdown & HTML report generation
├── email_sender.py              # Email sending
├── main.py                      # Main script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Customization

### Change Schedule

Edit `.github/workflows/weekly-digest.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Monday at 9 AM UTC
```

Cron format: `minute hour day-of-month month day-of-week`

Examples:
- `0 9 * * 1` - Every Monday at 9 AM
- `0 9 * * 1,4` - Monday and Thursday at 9 AM
- `0 9 1,15 * *` - 1st and 15th of each month at 9 AM

### Change Report Period

Default is 7 days. To change:

```bash
python main.py --report --days 14  # Last 14 days
```

In GitHub Actions, edit the workflow file:
```yaml
- name: Run scraper and send digest
  run: |
    python main.py --all --days 14
```

### Add More Sources

Edit `scrapers.py` and add a new scraper class:

```python
class NewSourceScraper(BaseScraper):
    def scrape(self) -> List[Dict]:
        # Your scraping logic
        pass
```

Then add it to the `NewsAggregator` class:

```python
self.scrapers = [
    # ... existing scrapers
    NewSourceScraper(user_agent),
]
```

## Troubleshooting

### Emails Not Sending

1. **Gmail**: Make sure you're using an App Password, not your regular password
2. **2FA**: Enable 2-factor authentication first
3. **Less Secure Apps**: App passwords work even with "less secure apps" disabled
4. **Check spam**: First emails might go to spam

### Scraping Errors

Some sites may block automated requests:
- The system uses proper user agents
- Includes retry logic with exponential backoff
- If a source consistently fails, it may have added CAPTCHA or blocking

### GitHub Actions Failing

1. Check secrets are set correctly
2. Verify workflow file syntax
3. Check Actions tab for error logs
4. Ensure repo is not private without enough minutes

## Local Development

Run tests:
```bash
# Scrape without email
python main.py --scrape

# Check what was found
python main.py --stats

# Generate report only
python main.py --report
```

## Database Schema

Articles are stored in SQLite with:
- `source`: News source name
- `title`: Article title
- `link`: URL (unique)
- `summary`: Article summary/excerpt
- `published_date`: Publication date (if available)
- `scraped_date`: When we found it

## Email Setup Guides

### Gmail
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create app password for "Mail"
5. Use that password in config

### Outlook/Hotmail
- SMTP: `smtp-mail.outlook.com`
- Port: `587`
- Use your regular password

### Other Providers
- Check your email provider's SMTP settings
- Most use port 587 with TLS

## Privacy & Security

- Config file with passwords is gitignored
- Secrets stored in GitHub Secrets (encrypted)
- No data sent to third parties except your email
- All processing happens in your repo

## License

MIT - Use freely!

## Contributing

Feel free to:
- Add more news sources
- Improve scrapers
- Enhance email templates
- Add features

## Support

Having issues?
1. Check the Troubleshooting section
2. Review GitHub Actions logs
3. Test locally first with `--scrape` flag
4. Verify your email config

---

**Happy tracking!** 🤖📰
