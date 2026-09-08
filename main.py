from fastapi import FastAPI
import requests
import re
import uvicorn

app = FastAPI(title="CNN Indonesia M3U8 Extractor")

TARGET_URL = "https://www.cnnindonesia.com/tv/embed?smartautoplay=true"

# Giả lập Header chính xác từ cURL của bạn
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "cache-control": "max-age=0",
    "cookie": "dtklucx=gen_ce319cda-3792-ec1c-8ede-3e81c316e6b8; cshx=a7f2d91b",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def fetch_m3u8_url():
    try:
        # Gửi request lấy HTML của trang embed
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html_content = response.text

        # Dùng Regex quét tìm toàn bộ URL có đuôi .m3u8 (bao gồm cả query parameters như wowzatoken)
        m3u8_pattern = r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*'
        matches = re.findall(m3u8_pattern, html_content)

        if matches:
            # Làm sạch URL nếu bị dính ký tự mã hóa html (&amp; -> &)
            clean_url = matches[0].replace("&amp;", "&")
            return clean_url
            
    except Exception as e:
        print(f"Lỗi khi gửi request: {e}")
    
    return None

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/get-stream")
def get_stream():
    m3u8_url = fetch_m3u8_url()
    if m3u8_url:
        return {
            "status": "success",
            "m3u8_url": m3u8_url
        }
    return {
        "status": "failed",
        "message": "Không tìm thấy đường dẫn m3u8 trong HTML"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
