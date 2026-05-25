from playwright.sync_api import sync_playwright



def ms_login(username: str, password: str, headless: bool = True) -> None:
    """妙手登录示例流程（选择器可能需按页面实际调整）。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.mychuang.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 以下为示例选择器，首次运行请按实际页面更新
        # page.click("text=登录")
        # page.fill("input[name='username']", username)
        # page.fill("input[name='password']", password)
        # page.click("button[type='submit']")

        print("页面已打开，请根据实际元素补全登录选择器。")

        context.close()
        browser.close()
