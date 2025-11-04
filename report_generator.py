"""
Generate markdown and email reports from AI news data
"""
from datetime import datetime
from typing import List, Dict
import os


class ReportGenerator:
    """Generates markdown reports from news articles"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

    def generate_markdown_report(self, articles: List[Dict], title: str = "AI News Digest") -> str:
        """Generate a markdown report from articles"""

        # Group articles by source
        by_source = {}
        for article in articles:
            source = article['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        # Generate markdown
        report_lines = [
            f"# {title}",
            f"",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"",
            f"**Total Articles:** {len(articles)}",
            f"",
            "---",
            ""
        ]

        # Table of contents
        report_lines.append("## Contents")
        report_lines.append("")
        for source in sorted(by_source.keys()):
            count = len(by_source[source])
            report_lines.append(f"- [{source}](#{source.lower().replace(' ', '-').replace('.', '')}) ({count} articles)")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # Articles by source
        for source in sorted(by_source.keys()):
            report_lines.append(f"## {source}")
            report_lines.append("")

            source_articles = by_source[source]

            if not source_articles:
                report_lines.append("*No new articles this week*")
                report_lines.append("")
                continue

            for article in source_articles:
                # Title with link
                report_lines.append(f"### [{article['title']}]({article['link']})")
                report_lines.append("")

                # Date
                if article.get('published_date'):
                    report_lines.append(f"**Published:** {article['published_date']}")
                    report_lines.append("")

                # Summary
                if article.get('summary'):
                    report_lines.append(article['summary'])
                    report_lines.append("")

                # Link
                report_lines.append(f"🔗 [Read more]({article['link']})")
                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

        return "\n".join(report_lines)

    def save_markdown_report(self, articles: List[Dict], filename: str = None) -> str:
        """Generate and save a markdown report"""
        if filename is None:
            filename = f"ai_news_{datetime.now().strftime('%Y-%m-%d')}.md"

        report_content = self.generate_markdown_report(articles)
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return filepath

    def generate_email_html(self, articles: List[Dict]) -> str:
        """Generate HTML email digest"""

        # Group articles by source
        by_source = {}
        for article in articles:
            source = article['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <meta charset='utf-8'>",
            "    <style>",
            "        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }",
            "        h2 { color: #2980b9; margin-top: 30px; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; }",
            "        h3 { color: #34495e; margin-top: 20px; }",
            "        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }",
            "        .stats { color: #7f8c8d; font-size: 14px; }",
            "        .article { margin-bottom: 30px; padding: 20px; background: #ffffff; border-left: 4px solid #3498db; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            "        .article-title { margin: 0 0 10px 0; }",
            "        .article-title a { color: #2c3e50; text-decoration: none; }",
            "        .article-title a:hover { color: #3498db; }",
            "        .article-date { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }",
            "        .article-summary { color: #555; margin-bottom: 15px; }",
            "        .article-link { display: inline-block; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }",
            "        .article-link:hover { background: #2980b9; }",
            "        .source-section { margin-bottom: 40px; }",
            "        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; color: #7f8c8d; font-size: 12px; text-align: center; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='header'>",
            "        <h1>🤖 AI News Digest</h1>",
            f"        <p class='stats'>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>",
            f"        <p class='stats'>Total articles: {len(articles)}</p>",
            "    </div>",
        ]

        # Articles by source
        for source in sorted(by_source.keys()):
            html_lines.append(f"    <div class='source-section'>")
            html_lines.append(f"        <h2>{source}</h2>")

            source_articles = by_source[source]

            if not source_articles:
                html_lines.append("        <p><em>No new articles this week</em></p>")
            else:
                for article in source_articles:
                    html_lines.append("        <div class='article'>")
                    html_lines.append(f"            <h3 class='article-title'><a href='{article['link']}'>{article['title']}</a></h3>")

                    if article.get('published_date'):
                        html_lines.append(f"            <p class='article-date'>📅 Published: {article['published_date']}</p>")

                    if article.get('summary'):
                        html_lines.append(f"            <p class='article-summary'>{article['summary']}</p>")

                    html_lines.append(f"            <a href='{article['link']}' class='article-link'>Read more →</a>")
                    html_lines.append("        </div>")

            html_lines.append("    </div>")

        html_lines.extend([
            "    <div class='footer'>",
            "        <p>This digest was automatically generated by your AI News Tracker</p>",
            "    </div>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_lines)
