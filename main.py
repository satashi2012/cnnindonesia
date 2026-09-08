import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI(title="CNN Indonesia M3U8 Extractor")
TARGET_URL = "https://www.cnnindonesia.com/tv/embed?smartautoplay=true"

async def scrape_m3u8_with_token():
    m3u8_urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--autoplay-policy=no-user-gesture-required"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://www.cnnindonesia.com/",
                "Origin": "https://www.cnnindonesia.com"
            }
        )
        page = await context.new_page()

        # Đưa link chứa wowzatoken lên đầu danh sách
        def handle_request(request):
            url = request.url
            if ".m3u8" in url:
                if "wowzatoken" in url or "livecnn-sec" in url:
                    m3u8_urls.insert(0, url)
                else:
                    m3u8_urls.append(url)

        page.on("request", handle_request)

        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            await page.mouse.click(300, 200) # Click kích hoạt player tạo token
            await page.wait_for_timeout(6000)
        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

    return m3u8_urls[0] if m3u8_urls else None

@app.get("/get-stream")
async def get_stream():
    url = await scrape_m3u8_with_token()
    if url:
        return {"status": "success", "m3u8_url": url}
    return {"status": "failed", "message": "Không tìm thấy token m3u8"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
