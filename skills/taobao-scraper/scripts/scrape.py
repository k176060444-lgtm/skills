#!/usr/bin/env python3
"""
淘宝爬取工具 - nodriver 反检测浏览器
支持：关键词搜索、商品详情页、扫码登录、cookie 持久化
"""

import argparse
import asyncio
import json
import os
import sys

# nodriver 在独立虚拟环境中
VENV_PYTHON = "/root/.openclaw/workspace/venvs/nodriver-env/bin/python3"
if not os.path.exists(VENV_PYTHON):
    print("ERROR: nodriver 虚拟环境不存在，请先安装", file=sys.stderr)
    sys.exit(1)

# 确保 nodriver 可用
try:
    import nodriver as uc
except ImportError:
    print("ERROR: nodriver 未安装，请执行: /root/.openclaw/workspace/venvs/nodriver-env/bin/pip install nodriver", file=sys.stderr)
    sys.exit(1)


DEFAULT_PROFILE = "/root/.openclaw/workspace/taobao_profile"
DEFAULT_WAIT = 10


async def ensure_login(browser, qr_screenshot=None):
    """确保登录态，未登录则截取二维码等待扫码"""
    page = await browser.get("https://login.taobao.com/member/login.jhtml")
    await page.sleep(6)

    cookies = await browser.cookies.get_all()
    cookie_names = [c.name for c in cookies]

    if "cookie1" in cookie_names or "unb" in cookie_names:
        print("LOGIN_OK: 已登录", file=sys.stderr)
        return True

    # 需要登录
    if qr_screenshot:
        await page.save_screenshot(qr_screenshot, full_page=True)
        print(f"QR_SAVED: {qr_screenshot}", file=sys.stderr)
    else:
        print("QR_READY: 请用淘宝APP扫码登录", file=sys.stderr)

    # 等待扫码（最多 5 分钟）
    for i in range(300):
        await page.sleep(3)
        cookies = await browser.cookies.get_all()
        cookie_names = [c.name for c in cookies]
        if "cookie1" in cookie_names or "unb" in cookie_names:
            print("LOGIN_SUCCESS: 扫码登录成功", file=sys.stderr)
            return True

    print("LOGIN_TIMEOUT: 扫码超时", file=sys.stderr)
    return False


async def dismiss_login_popup(page):
    """处理"确认登录"弹窗"""
    try:
        btn = await page.find("快速进入", best_match=True)
        if btn:
            await btn.click()
            await page.sleep(3)
            print("POPUP_DISMISSED: 已点击快速进入", file=sys.stderr)
            return True
    except Exception:
        pass
    return False


async def scroll_page(page, times=5):
    """滚动页面触发懒加载"""
    for _ in range(times):
        await page.scroll_down(500)
        await page.sleep(1)


async def extract_page_data(page):
    """提取页面数据"""
    text = await page.evaluate('document.body?.innerText || ""')
    url = await page.evaluate("window.location.href")
    title = await page.evaluate("document.title")
    return {"url": url, "title": title, "text": text}


async def taobao_search(browser, keyword, wait=DEFAULT_WAIT, screenshot=None):
    """淘宝搜索"""
    print(f"SEARCH: {keyword}", file=sys.stderr)
    page = await browser.get(f"https://s.taobao.com/search?q={keyword}")
    await page.sleep(wait)

    # 处理登录弹窗
    await dismiss_login_popup(page)

    # 滚动加载
    await scroll_page(page)

    # 提取数据
    data = await extract_page_data(page)

    # 检查是否成功
    if "亲，请登录" in data["text"] and len(data["text"]) < 500:
        print("ERROR: 搜索需要登录，请先执行 --login", file=sys.stderr)
        return None

    if screenshot:
        await page.save_screenshot(screenshot, full_page=True)
        print(f"SCREENSHOT: {screenshot}", file=sys.stderr)

    return data


async def resolve_mobile_tmall(browser, url, wait=DEFAULT_WAIT):
    """处理手机天猫短链，转换为桌面版URL"""
    page = await browser.get(url)
    await page.sleep(8)
    final_url = await page.evaluate("window.location.href")

    # 如果跳转到了 tmallx.tmall.com（移动版），提取ID转桌面版
    if "tmallx.tmall.com" in final_url and "id=" in final_url:
        item_id = final_url.split("id=")[1].split("&")[0]
        desktop_url = f"https://detail.tmall.com/item.htm?id={item_id}"
        print(f"MOBILE_TMFIX: {final_url[:60]}... -> {desktop_url}", file=sys.stderr)
        return desktop_url

    # 如果跳转到了 m.taobao.com（移动版），提取ID转桌面版
    if "m.taobao.com" in final_url and "id=" in final_url:
        item_id = final_url.split("id=")[1].split("&")[0]
        desktop_url = f"https://item.taobao.com/item.htm?id={item_id}"
        print(f"MOBILE_TBFIX: {final_url[:60]}... -> {desktop_url}", file=sys.stderr)
        return desktop_url

    return final_url  # 已经是桌面版，直接用


async def taobao_product(browser, url, wait=DEFAULT_WAIT, screenshot=None):
    """淘宝/天猫商品详情页"""
    print(f"PRODUCT: {url}", file=sys.stderr)

    # 先访问短链获取跳转目标，处理移动版转换
    resolved_url = await resolve_mobile_tmall(browser, url, wait)

    # 如果转换了URL，需要重新访问桌面版
    page = await browser.get(resolved_url)
    await page.sleep(wait)

    # 处理登录弹窗
    await dismiss_login_popup(page)

    # 滚动加载详情
    await scroll_page(page, times=3)

    # 提取数据
    data = await extract_page_data(page)

    # 检查跳转后的URL
    final_url = await page.evaluate("window.location.href")
    data["final_url"] = final_url

    if screenshot:
        await page.save_screenshot(screenshot, full_page=True)
        print(f"SCREENSHOT: {screenshot}", file=sys.stderr)

    return data


async def main():
    parser = argparse.ArgumentParser(description="淘宝爬取工具（nodriver）")
    parser.add_argument("--login", action="store_true", help="首次扫码登录模式")
    parser.add_argument("--search", type=str, help="搜索关键词")
    parser.add_argument("--url", type=str, help="商品详情页链接")
    parser.add_argument("--screenshot", type=str, help="截图保存路径")
    parser.add_argument("--output", type=str, help="文本保存路径")
    parser.add_argument("--profile", type=str, default=DEFAULT_PROFILE, help="cookie 持久化目录")
    parser.add_argument("--wait", type=int, default=DEFAULT_WAIT, help="页面等待秒数")
    args = parser.parse_args()

    if not args.login and not args.search and not args.url:
        parser.print_help()
        sys.exit(1)

    # 确保 profile 目录存在
    os.makedirs(args.profile, exist_ok=True)

    # 启动浏览器
    browser = await uc.start(
        headless=True,
        no_sandbox=True,
        user_data_dir=args.profile,
    )

    try:
        # 登录模式
        if args.login:
            qr_path = args.screenshot or os.path.join(args.profile, "qr_login.png")
            success = await ensure_login(browser, qr_screenshot=qr_path)
            if success:
                print("LOGIN_COMPLETE: 登录完成，可正常使用", file=sys.stderr)
            else:
                print("LOGIN_FAILED: 登录失败", file=sys.stderr)
                sys.exit(1)

        # 搜索模式
        elif args.search:
            # 确保已登录
            cookies = await browser.cookies.get_all()
            if "cookie1" not in [c.name for c in cookies]:
                print("NOT_LOGGED_IN: 未登录，请先执行 --login", file=sys.stderr)
                sys.exit(1)

            data = await taobao_search(
                browser, args.search,
                wait=args.wait,
                screenshot=args.screenshot,
            )
            if data:
                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(data["text"])
                    print(f"SAVED: {args.output}", file=sys.stderr)
                else:
                    print(data["text"])

        # 商品详情模式
        elif args.url:
            cookies = await browser.cookies.get_all()
            if "cookie1" not in [c.name for c in cookies]:
                print("NOT_LOGGED_IN: 未登录，请先执行 --login", file=sys.stderr)
                sys.exit(1)

            data = await taobao_product(
                browser, args.url,
                wait=args.wait,
                screenshot=args.screenshot,
            )
            if data:
                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(data["text"])
                    print(f"SAVED: {args.output}", file=sys.stderr)
                else:
                    print(data["text"])

    finally:
        browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
