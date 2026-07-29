import os
import requests
from bs4 import BeautifulSoup

URL = "https://kmznw210-sasa.github.io/alert-hangangriver_boat/"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_message(message):
    """디스코드 웹훅 메시지 전송 함수"""
    if not DISCORD_WEBHOOK_URL:
        print("[오류] DISCORD_WEBHOOK_URL 설정되지 않았습니다.")
        return

    payload = {
        "content": message
    }
    
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        res.raise_for_status()
        print("[성공] 디스코드 알림 전송 완료")
    except Exception as e:
        print(f"[오류] 디스코드 전송 실패: {e}")

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        is_sold_out = False
        text_content = soup.get_text()
        
        # 품절 및 매진 문구 확인
        if "품절" in text_content or "매진" in text_content or "SOLD OUT" in text_content.upper():
            is_sold_out = True
            
        buy_button = soup.select_one("a.btn-buy, button.btn-buy, .buy_btn")
        if buy_button and ("disabled" in buy_button.get("class", []) or buy_button.get("disabled") is not None):
            is_sold_out = True

        if not is_sold_out:
            message = (
                "🚨 **[취소표/잔여자리 발생 알림]**\n"
                "대회 참가신청 자리가 발생했습니다!\n"
                f"지금 즉시 신청하세요: {URL}"
            )
            print("[감지] 취소표 발생! 디스코드 알림을 전송합니다.")
            send_discord_message(message)
        else:
            print("[상태] 현재 계속 품절 상태입니다.")

    except Exception as e:
        print(f"[오류] 페이지 확인 중 에러 발생: {e}")

if __name__ == "__main__":
    check_stock()
