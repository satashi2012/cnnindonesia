import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI(title="M3U8 Extractor API")
TARGET_URL = "https://www.cnnindonesia.com/tv/embed?smartautoplay=true"

async def scrape_m3u8_links():
    m3u8_urls = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--autoplay-policy=no-user-gesture-required" # Cho phép tự động phát video
            ]
        )

        # Thêm Referer để bypass kiểm tra của server CNN
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://www.cnnindonesia.com/",
                "Origin": "https://www.cnnindonesia.com"
            }
        )

        page = await context.new_page()

        def handle_request(request):
            if ".m3u8" in request.url:
                print(f"[LOG] Đã tìm thấy: {request.url}")
                m3u8_urls.append(request.url)

        page.on("request", handle_request)

        try:
            print("[LOG] Đang tải trang...")
            # Đợi trang tải xong và mạng ổn định
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)
            
            # Chờ thêm 10 giây để chắc chắn player đã gọi file m3u8
            print("[LOG] Đang chờ player load video...")
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"[LOG] Lỗi: {e}")
        finally:
            await browser.close()

    return list(dict.fromkeys(m3u8_urls))

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/get-stream")
async def get_stream():
    urls = await scrape_m3u8_links()
    if urls:
        return {
            "status": "success",
            "m3u8_url": urls[0],
            "all_found": urls
        }
    return {"status": "failed", "message": "Không tìm thấy đường dẫn m3u8"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
