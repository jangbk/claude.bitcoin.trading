"""
빗썸 비트코인 자동매매 봇 v5.2
40/100 MA 크로스오버 + 100 MA 시장 필터
+ 텔레그램 매시간 알림 + 일일 리포트

사용법:
1. .env 파일에 API 키 설정
2. python bithumb_trading_bot.py 실행
"""

import pybithumb
import pandas as pd
import numpy as np
import time
import logging
import schedule
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# ============================================================================
# 로깅 설정
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 설정
# ============================================================================
class Config:
    # 전략 파라미터 (최적화 완료)
    FAST_MA = 40
    SLOW_MA = 100
    FILTER_MA = 100

    # 거래 설정
    TICKER = "BTC"              # 거래 종목
    TRADE_AMOUNT_PERCENT = 0.70 # 잔고의 70% 사용
    MIN_TRADE_AMOUNT = 10000    # 최소 거래 금액 (원)

    # 실행 주기 (분)
    CHECK_INTERVAL = 60         # 1시간마다 체크 (일봉 전략이므로)

    # 테스트 모드 (True: 실제 주문 안 함)
    TEST_MODE = False

    # 텔레그램 알림 설정
    TELEGRAM_ENABLED = True
    TELEGRAM_TOKEN = ""
    TELEGRAM_CHAT_ID = ""

    # 알림 설정
    HOURLY_REPORT = True        # 매시간 상태 알림
    DAILY_REPORT = True         # 일일 리포트 (09:00 KST)


# ============================================================================
# 텔레그램 알림
# ============================================================================
def send_telegram(message: str):
    """텔레그램으로 알림 전송"""
    if not Config.TELEGRAM_ENABLED:
        return

    # .env에서 토큰 읽기
    token = os.getenv("TELEGRAM_TOKEN", Config.TELEGRAM_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", Config.TELEGRAM_CHAT_ID)

    if not token or not chat_id:
        logger.warning("텔레그램 설정이 없습니다.")
        return

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info("📱 텔레그램 알림 전송 완료")
        else:
            logger.error(f"텔레그램 전송 실패: {response.text}")
    except Exception as e:
        logger.error(f"텔레그램 오류: {e}")


# ============================================================================
# 빗썸 API 클래스
# ============================================================================
class BithumbTrader:
    def __init__(self, api_key: str, api_secret: str):
        """빗썸 트레이더 초기화"""
        self.bithumb = pybithumb.Bithumb(api_key, api_secret)
        self.ticker = Config.TICKER
        self.position = None  # 'long' or None
        self.entry_price = 0  # 진입 가격
        self.entry_time = None  # 진입 시간

        logger.info("=" * 60)
        logger.info("🤖 빗썸 자동매매 봇 v5.2 시작")
        logger.info(f"   전략: {Config.FAST_MA}/{Config.SLOW_MA} MA + {Config.FILTER_MA} MA 필터")
        logger.info(f"   종목: {self.ticker}")
        logger.info(f"   테스트 모드: {Config.TEST_MODE}")
        logger.info("=" * 60)

    def get_ohlcv(self, days: int = 200) -> pd.DataFrame:
        """일봉 데이터 조회"""
        try:
            df = pybithumb.get_ohlcv(self.ticker, interval="day")
            if df is None or df.empty:
                logger.error("OHLCV 데이터 조회 실패")
                return None
            return df.tail(days)
        except Exception as e:
            logger.error(f"OHLCV 조회 오류: {e}")
            return None

    def calculate_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """이동평균 계산"""
        df = df.copy()
        df['fast_ma'] = df['close'].rolling(window=Config.FAST_MA).mean()
        df['slow_ma'] = df['close'].rolling(window=Config.SLOW_MA).mean()
        df['filter_ma'] = df['close'].rolling(window=Config.FILTER_MA).mean()
        return df

    def check_signal(self, df: pd.DataFrame) -> str:
        """매매 신호 확인"""
        if df is None or len(df) < Config.SLOW_MA + 1:
            return "hold"

        current = df.iloc[-1]
        previous = df.iloc[-2]

        price = current['close']
        fast_ma = current['fast_ma']
        slow_ma = current['slow_ma']
        filter_ma = current['filter_ma']

        prev_fast_ma = previous['fast_ma']
        prev_slow_ma = previous['slow_ma']

        # 시장 필터: 가격이 100 MA 위에 있어야 함
        market_bullish = price > filter_ma

        # 골든 크로스: fast MA가 slow MA를 상향 돌파
        golden_cross = (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)

        # 데드 크로스: fast MA가 slow MA를 하향 돌파
        death_cross = (prev_fast_ma >= prev_slow_ma) and (fast_ma < slow_ma)

        # 필터 이탈
        filter_exit = not market_bullish

        logger.info(f"📊 현재 상태:")
        logger.info(f"   가격: {price:,.0f}원")
        logger.info(f"   Fast MA({Config.FAST_MA}): {fast_ma:,.0f}")
        logger.info(f"   Slow MA({Config.SLOW_MA}): {slow_ma:,.0f}")
        logger.info(f"   Filter MA({Config.FILTER_MA}): {filter_ma:,.0f}")
        logger.info(f"   시장 상태: {'강세' if market_bullish else '약세'}")

        # 상태 저장 (알림용)
        self.last_price = price
        self.last_fast_ma = fast_ma
        self.last_slow_ma = slow_ma
        self.last_filter_ma = filter_ma
        self.last_market_status = '강세' if market_bullish else '약세'

        if golden_cross and market_bullish:
            return "buy"
        elif death_cross or filter_exit:
            return "sell"
        else:
            return "hold"

    def get_balance(self) -> dict:
        """잔고 조회"""
        try:
            krw = self.bithumb.get_balance(self.ticker)[2]  # 원화 잔고
            btc = self.bithumb.get_balance(self.ticker)[0]  # BTC 잔고
            return {"KRW": krw, "BTC": btc}
        except Exception as e:
            logger.error(f"잔고 조회 오류: {e}")
            return {"KRW": 0, "BTC": 0}

    def buy(self) -> bool:
        """매수 실행"""
        try:
            balance = self.get_balance()
            krw = balance["KRW"]

            if krw < Config.MIN_TRADE_AMOUNT:
                logger.warning(f"잔고 부족: {krw:,.0f}원")
                return False

            # 매수 금액 계산
            trade_amount = krw * Config.TRADE_AMOUNT_PERCENT

            logger.info(f"🟢 매수 신호!")
            logger.info(f"   매수 금액: {trade_amount:,.0f}원")

            if Config.TEST_MODE:
                logger.info("   [테스트 모드] 실제 주문 없음")
                self.position = "long"
                return True

            # 시장가 매수
            result = self.bithumb.buy_market_order(self.ticker, trade_amount)

            if result:
                logger.info(f"   ✅ 매수 완료: {result}")
                self.position = "long"
                self.entry_price = self.last_price
                self.entry_time = datetime.now()
                # 텔레그램 알림
                send_telegram(f"🟢 <b>매수 완료!</b>\n금액: {trade_amount:,.0f}원\n가격: {self.last_price:,.0f}원\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                return True
            else:
                logger.error("   ❌ 매수 실패")
                send_telegram("❌ 매수 실패!")
                return False

        except Exception as e:
            logger.error(f"매수 오류: {e}")
            send_telegram(f"⚠️ 매수 오류: {e}")
            return False

    def sell(self) -> bool:
        """매도 실행"""
        try:
            balance = self.get_balance()
            btc = balance["BTC"]

            if btc <= 0:
                logger.warning("매도할 BTC 없음")
                return False

            # 현재가 조회
            current_price = pybithumb.get_current_price(self.ticker)
            sell_value = btc * current_price

            logger.info(f"🔴 매도 신호!")
            logger.info(f"   매도 수량: {btc:.8f} BTC")
            logger.info(f"   예상 금액: {sell_value:,.0f}원")

            if Config.TEST_MODE:
                logger.info("   [테스트 모드] 실제 주문 없음")
                self.position = None
                return True

            # 시장가 매도
            result = self.bithumb.sell_market_order(self.ticker, btc)

            if result:
                logger.info(f"   ✅ 매도 완료: {result}")
                # 수익률 계산
                profit_pct = ((current_price - self.entry_price) / self.entry_price * 100) if self.entry_price > 0 else 0
                self.position = None
                # 텔레그램 알림
                send_telegram(f"🔴 <b>매도 완료!</b>\n수량: {btc:.8f} BTC\n금액: {sell_value:,.0f}원\n수익률: {profit_pct:+.2f}%\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                self.entry_price = 0
                return True
            else:
                logger.error("   ❌ 매도 실패")
                send_telegram("❌ 매도 실패!")
                return False

        except Exception as e:
            logger.error(f"매도 오류: {e}")
            send_telegram(f"⚠️ 매도 오류: {e}")
            return False

    def send_hourly_report(self):
        """매시간 상태 알림"""
        if not Config.HOURLY_REPORT:
            return

        try:
            balance = self.get_balance()
            current_price = pybithumb.get_current_price(self.ticker)

            # 포지션 상태
            if self.position == "long" and balance["BTC"] > 0:
                btc_value = balance["BTC"] * current_price
                profit_pct = ((current_price - self.entry_price) / self.entry_price * 100) if self.entry_price > 0 else 0
                position_str = f"🟢 롱 포지션\n   평가금액: {btc_value:,.0f}원\n   수익률: {profit_pct:+.2f}%"
            else:
                position_str = "⚪ 포지션 없음 (현금 보유)"

            msg = f"""⏰ <b>매시간 상태 알림</b>
━━━━━━━━━━━━━━━
📊 BTC: {current_price:,.0f}원
📈 40 MA: {self.last_fast_ma:,.0f}
📉 100 MA: {self.last_slow_ma:,.0f}
🎯 시장: {self.last_market_status}
━━━━━━━━━━━━━━━
{position_str}
💰 원화: {balance['KRW']:,.0f}원
━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%m/%d %H:%M')}"""

            send_telegram(msg)
        except Exception as e:
            logger.error(f"매시간 알림 오류: {e}")

    def send_daily_report(self):
        """일일 리포트 (09:00 KST)"""
        if not Config.DAILY_REPORT:
            return

        try:
            balance = self.get_balance()
            current_price = pybithumb.get_current_price(self.ticker)

            # 총 자산 계산
            btc_value = balance["BTC"] * current_price
            total_value = balance["KRW"] + btc_value

            # 24시간 가격 변동 (근사치)
            df = self.get_ohlcv(2)
            if df is not None and len(df) >= 2:
                yesterday_price = df.iloc[-2]['close']
                price_change = ((current_price - yesterday_price) / yesterday_price) * 100
                price_change_str = f"{price_change:+.2f}%"
            else:
                price_change_str = "N/A"

            # 포지션 상태
            if self.position == "long" and balance["BTC"] > 0:
                position_str = f"🟢 롱 포지션 보유 중\n   BTC: {balance['BTC']:.8f}\n   평가: {btc_value:,.0f}원"
            else:
                position_str = "⚪ 포지션 없음 (매수 대기)"

            msg = f"""📋 <b>일일 리포트</b>
━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y년 %m월 %d일')}
━━━━━━━━━━━━━━━
💹 <b>BTC 현황</b>
   현재가: {current_price:,.0f}원
   24H 변동: {price_change_str}

📊 <b>이동평균</b>
   40 MA: {self.last_fast_ma:,.0f}
   100 MA: {self.last_slow_ma:,.0f}
   시장: {self.last_market_status}

💼 <b>포지션</b>
{position_str}

💰 <b>자산 현황</b>
   원화: {balance['KRW']:,.0f}원
   BTC 평가: {btc_value:,.0f}원
   <b>총 자산: {total_value:,.0f}원</b>
━━━━━━━━━━━━━━━
🤖 빗썸 자동매매 봇 v5.2"""

            send_telegram(msg)
        except Exception as e:
            logger.error(f"일일 리포트 오류: {e}")

    def run(self):
        """메인 실행 로직"""
        logger.info("\n" + "=" * 40)
        logger.info(f"⏰ 체크 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 데이터 조회
        df = self.get_ohlcv()
        if df is None:
            return

        # 2. 이동평균 계산
        df = self.calculate_ma(df)

        # 3. 신호 확인
        signal = self.check_signal(df)
        logger.info(f"📈 신호: {signal.upper()}")

        # 4. 매매 실행
        if signal == "buy" and self.position != "long":
            self.buy()
        elif signal == "sell" and self.position == "long":
            self.sell()
        else:
            logger.info("   현재 포지션 유지")

        # 5. 현재 잔고 출력
        balance = self.get_balance()
        logger.info(f"💰 잔고: {balance['KRW']:,.0f}원 / {balance['BTC']:.8f} BTC")

        # 6. 매시간 알림 전송
        self.send_hourly_report()


# ============================================================================
# 메인 실행
# ============================================================================
def main():
    # 환경변수 로드
    load_dotenv()

    api_key = os.getenv("BITHUMB_API_KEY")
    api_secret = os.getenv("BITHUMB_API_SECRET")

    # 테스트 모드에서는 API 키 없이도 실행 가능
    if Config.TEST_MODE:
        if not api_key or api_key == "여기에_API_KEY_입력":
            logger.warning("⚠️ API 키 미설정 - 테스트 모드로 실행 (데이터 조회만 가능)")
            api_key = ""
            api_secret = ""
    else:
        if not api_key or not api_secret or api_key == "여기에_API_KEY_입력":
            logger.error("❌ API 키가 설정되지 않았습니다!")
            logger.error("   .env 파일에 BITHUMB_API_KEY와 BITHUMB_API_SECRET를 설정하세요.")
            logger.info("\n📝 .env 파일 예시:")
            logger.info("   BITHUMB_API_KEY=your_api_key_here")
            logger.info("   BITHUMB_API_SECRET=your_api_secret_here")
            return

    # 트레이더 초기화
    trader = BithumbTrader(api_key, api_secret)

    # 첫 실행
    trader.run()

    # 스케줄 설정
    schedule.every().hour.at(":00").do(trader.run)  # 매 시간 정각
    schedule.every().day.at("00:00").do(trader.send_daily_report)  # 09:00 KST (00:00 UTC)

    logger.info(f"\n🔄 스케줄러 시작")
    logger.info("   - 매 시간 정각: 시장 체크 + 상태 알림")
    logger.info("   - 매일 09:00 KST: 일일 리포트")
    logger.info("   종료하려면 Ctrl+C를 누르세요.\n")

    # 시작 알림
    send_telegram("🤖 <b>빗썸 자동매매 봇 시작!</b>\n\n✅ 매시간 상태 알림 ON\n✅ 일일 리포트 ON (09:00)")

    # 스케줄 루프
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n👋 봇 종료")
            send_telegram("👋 봇이 종료되었습니다.")
            break


if __name__ == "__main__":
    main()
