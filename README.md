# 🤖 비트코인 자동매매 봇 v5.1

40/100 MA 크로스오버 + 100 MA 시장 필터 전략을 사용한 빗썸 자동매매 봇

## 📊 백테스트 결과 (2017-2026)

| 항목 | 결과 |
|------|------|
| 총 수익률 | **1,751%** |
| Buy & Hold | 1,078% |
| 연평균 수익률 | 41.37% |
| 승률 | 58.33% |
| Profit Factor | 11.14 |
| 최대 손실폭 | -49.59% |

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git
cd bitcoin-trading-bot
pip install -r requirements_trading.txt
```

### 2. API 키 설정

```bash
cp .env.example .env
nano .env  # API 키 입력
```

### 3. 실행

```bash
# 테스트 모드
python3 bithumb_trading_bot.py

# 실제 매매 (TEST_MODE = False 변경 후)
python3 bithumb_trading_bot.py
```

## 📁 파일 구조

```
├── bithumb_trading_bot.py    # 메인 봇 코드
├── bitcoin_backtest.py       # 백테스트 코드
├── bitcoin_strategy_v5.1.pine # TradingView Pine Script
├── requirements_trading.txt  # 필요 라이브러리
├── .env.example             # 환경변수 예시
└── README.md
```

## ⚙️ 전략 파라미터

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| Fast MA | 40 | 빠른 이동평균 |
| Slow MA | 100 | 느린 이동평균 |
| Filter MA | 100 | 시장 필터 MA |

## 📋 매매 규칙

1. **매수 조건**: Fast MA가 Slow MA 상향 돌파 + 가격이 Filter MA 위
2. **매도 조건**: Fast MA가 Slow MA 하향 돌파 또는 가격이 Filter MA 아래

## 🖥️ 24시간 서버 실행

### systemd 서비스 등록

```bash
sudo cp trading-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

### 상태 확인

```bash
sudo systemctl status trading-bot
journalctl -u trading-bot -f
```

## 📱 알림 설정

Telegram 또는 Discord를 통해 매매 알림을 받을 수 있습니다.
자세한 설정은 `bithumb_trading_bot.py`의 알림 섹션을 참고하세요.

## ⚠️ 주의사항

- 투자 손실의 책임은 사용자에게 있습니다
- 반드시 테스트 모드로 충분히 테스트 후 사용하세요
- API 출금 권한은 비활성화를 권장합니다
- 소액으로 시작하세요

## 📜 라이선스

MIT License

---

**버전**: 5.1 (최적화됨)
**기반**: Python 백테스트 파라미터 최적화
**지원 거래소**: 빗썸 (Bithumb)
