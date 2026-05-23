#!/usr/bin/env python3
"""
xianyu-scraper - 高反爬网站 Playwright 爬取脚本
用法: python3 scrape.py '<URL>'
     python3 scrape.py '<URL>' --scroll 10

依赖: pip install playwright && playwright install chromium
"""
import sys
import json
import argparse


def scrape(url: str, scroll_times: int = 10, timeout: int = 35000):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
        ])
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        page = context.new_page()
        page.add_init_script("delete navigator.__proto__.webdriver;")

        page.goto(url, timeout=timeout)
        page.wait_for_timeout(5000)

        for i in range(scroll_times):
            page.mouse.move(720, 300 + i * 50)
            page.wait_for_timeout(500)
            page.evaluate(f'window.scrollBy(0, {200 + i * 100})')
            page.wait_for_timeout(500)

        text = page.inner_text('body')
        browser.close()
        return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='高反爬网站爬取')
    parser.add_argument('url', help='目标 URL')
    parser.add_argument('--scroll', type=int, default=10, help='滚动次数（默认10）')
    parser.add_argument('--timeout', type=int, default=35000, help='超时毫秒（默认35000）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认打印到stdout）')
    args = parser.parse_args()

    try:
        text = scrape(args.url, scroll_times=args.scroll, timeout=args.timeout)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f'已保存到 {args.output}')
        else:
            print(text)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
