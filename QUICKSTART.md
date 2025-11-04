# Quick Start Guide

Get your AI News Tracker running in 5 minutes!

## For Local Use (Testing)

### Step 1: Install Dependencies

```bash
cd ai-news-tracker
pip install -r requirements.txt
```

### Step 2: Configure Email

```bash
cp config.example.ini config.ini
```

Edit `config.ini` with your email:

```ini
[email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = YOUR_EMAIL@gmail.com
sender_password = YOUR_APP_PASSWORD
recipient_email = YOUR_EMAIL@gmail.com
```

**Gmail App Password**: https://myaccount.google.com/apppasswords

### Step 3: Test Setup

```bash
python test_setup.py
```

### Step 4: Run It!

```bash
python main.py --all
```

Check your email for the digest!

---

## For GitHub Actions (Automated Weekly)

### Step 1: Create GitHub Repo

```bash
cd ai-news-tracker
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-news-tracker.git
git push -u origin main
```

### Step 2: Add Secrets

Go to: **Your Repo → Settings → Secrets and variables → Actions**

Click "New repository secret" for each:

| Secret Name | Example Value |
|-------------|---------------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SENDER_EMAIL` | `you@gmail.com` |
| `SENDER_PASSWORD` | Your app password |
| `RECIPIENT_EMAIL` | `you@gmail.com` |

### Step 3: Enable Actions

Go to: **Actions tab → I understand my workflows, go ahead and enable them**

### Step 4: Test Run

**Actions tab → Weekly AI News Digest → Run workflow**

Wait 1-2 minutes, check your email!

---

## Customization

### Change Schedule

Edit `.github/workflows/weekly-digest.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

Examples:
- `0 9 * * 1,4` - Monday and Thursday
- `0 9 1 * *` - First day of each month

### Change Report Days

```bash
python main.py --all --days 14  # Last 14 days instead of 7
```

---

## Troubleshooting

**Email not sending?**
- Gmail: Use App Password, not regular password
- Enable 2FA first: https://myaccount.google.com/security
- Then create App Password: https://myaccount.google.com/apppasswords

**GitHub Actions failing?**
- Check all 5 secrets are set
- View logs in Actions tab
- Try running locally first

**No articles found?**
- Some sources may be temporarily down
- Check output for specific errors
- Run `python main.py --stats` to see what's stored

---

## Common Commands

```bash
# Full run (scrape + report + email)
python main.py --all

# Just scrape (no email)
python main.py --scrape

# Just report (from existing data)
python main.py --report

# Show statistics
python main.py --stats

# Test your setup
python test_setup.py
```

---

**Need help?** Check the full README.md
