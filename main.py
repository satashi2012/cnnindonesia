import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI(title="M3U8 Extractor API")

TARGET_URL = "https://www.cnnindonesia.com/tv/embed?smartautoplay=true"

async def scrape_m3u8_links():
    m3u8_urls = []

    async with async_playwright() as p:
        # Khởi chạy Chromium ở chế độ Headless
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
            ]
        )

        # Cấu hình Context mô phỏng trình duyệt thật và giả lập Headers
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            extra_http_headers={
                "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.6,en;q=0.5",
                "cache-control": "max-age=0",
                "cookie": "dtklucx=gen_ce319cda-3792-ec1c-8ede-3e81c316e6b8; cshx=a7f2d91b",
            }
        )

        page = await context.new_page()

        # Bắt sự kiện request mạng để tìm URL .m3u8
        def handle_request(request):
            if ".m3u8" in request.url:
                m3u8_urls.append(request.url)

        page.on("request", handle_request)

        try:
            # Điều hướng tới trang embed
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            
            # Chờ 5 giây để Player khởi chạy và gọi file manifest .m3u8
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Lỗi khi tải trang: {e}")
        finally:
            await browser.close()

    # Loại bỏ trùng lặp nếu có
    return list(dict.fromkeys(m3u8_urls))

@app.get("/")
async def root():
    return {"status": "ok", "message": "M3U8 Scraper API đang hoạt động"}

@app.get("/get-stream")
async def get_stream():
    urls = await scrape_m3u8_links()
    if urls:
        return {
            "status": "success",
            "m3u8_url": urls[0],
            "all_found": urls
        }
    return {
        "status": "failed",
        "message": "Không tìm thấy đường dẫn m3u8"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
