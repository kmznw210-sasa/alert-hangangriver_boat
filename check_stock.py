import os
import time
import requests
from bs4 import BeautifulSoup

URL = "https://urbansports.kr/shop_view?idx=137"  # 감지 대상 URL
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_message(message):
    if not DISCORD_WEBHOOK_URL:
        print("[오류] DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
        return
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[오류] 디스코드 발송 실패: {e}")

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 버튼 및 품절 로직 검사
    buy_button = soup.select_one(".btn_buy, .buy_btn, .btn-buy, a[href*='order']")
    is_sold_out = False

    if buy_button:
        button_text = buy_button.get_text().strip()
        if "품절" in button_text or "매진" in button_text or "SOLD OUT" in button_text.upper():
            is_sold_out = True
        elif "disabled" in buy_button.get("class", []) or buy_button.get("disabled") is not None:
            is_sold_out = True
    else:
        is_sold_out = True

    if not is_sold_out:
        print("[감지] 취소표 발생! 디스코드 알림을 전송합니다.")
        send_discord_message(f"🚨 **[취소표 발생 알림]** 지금 즉시 신청하세요: {URL}")
    else:
        print("[상태] 품절 상태 유지 중...")

if __name__ == "__main__":
    # 총 5시간 50분 동안 5분(300초) 간격으로 70회 반복 실행 후 종료
    # (GitHub Actions 한계 시간인 6시간을 넘지 않도록 안전하게 설정)
    TOTAL_RUNS = 70 
    INTERVAL = 300  # 300초 = 5분

    print(f"[시작] GitHub Actions 내부 루프 실행 (5분 간격, 총 {TOTAL_RUNS}회 수행)")

    for i in range(1, TOTAL_RUNS + 1):
        print(f"\n--- [{i}/{TOTAL_RUNS}번째 검사 실행] ---")
        try:
            check_stock()
        except Exception as e:
            print(f"[오류 발생]: {e}")
        
        # 마지막 회차에서는 대기하지 않고 종료
        if i < TOTAL_RUNS:
            time.sleep(INTERVAL)

    print("[완료] 이번 워크플로우 루프 실행이 완료되었습니다.")
