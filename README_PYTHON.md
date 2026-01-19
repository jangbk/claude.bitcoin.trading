# 비트코인 자동매매 전략 - Python 버전 설정

## 필요한 라이브러리 설치

```bash
# 필수 라이브러리 설치
pip install backtesting yfinance pandas numpy matplotlib

# 또는 한 번에
pip install backtesting yfinance pandas numpy matplotlib
```

## 파일 구조

```
Bitcoin Autotrading_Trading View_Pine Script/
├── bitcoin_auto_trading.pine      # Pine Script 버전 (TradingView)
├── bitcoin_backtest.py             # Python 백테스트 버전
├── requirements.txt                # Python 패키지 목록
└── README.md                       # 사용 가이드
```

## 사용 방법

### 1. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 백테스트 실행

```bash
python bitcoin_backtest.py
```

### 3. 결과 확인

실행하면 자동으로:
- 📥 비트코인 데이터 다운로드
- 🚀 백테스트 실행
- 📊 결과 통계 출력
- 📈 차트 생성

## Python vs Pine Script

### Pine Script (TradingView)
**장점**:
- ✅ 시각화 우수
- ✅ GUI로 즉시 확인
- ✅ 설정 불필요
- ✅ 클라우드 기반

**단점**:
- ❌ 제한된 데이터 접근
- ❌ 실제 거래 불가
- ❌ 복잡한 로직 어려움

### Python
**장점**:
- ✅ 완전한 제어
- ✅ 외부 데이터 연동
- ✅ 실제 거래 가능
- ✅ 머신러닝 적용 가능
- ✅ 커스터마이징 자유

**단점**:
- ❌ 설정 필요
- ❌ 코딩 필요
- ❌ 로컬 실행

## 파라미터 조정

`bitcoin_backtest.py` 파일에서:

```python
class MA_Filter_Strategy(Strategy):
    # 이 값들을 변경하여 테스트
    fast_ma = 50              # 빠른 이동평균
    slow_ma = 55              # 느린 이동평균
    market_filter_ma = 200    # 시장 필터
    use_market_filter = True  # 필터 사용 여부
```

## 다른 기간 테스트

```python
# main() 함수에서 날짜 변경
btc_data = download_btc_data(
    start_date='2021-01-01',  # 시작일
    end_date='2021-04-30'      # 종료일
)
```

## 파라미터 최적화

```python
# 백테스트 후 최적화 실행 (주의: 시간 오래 걸림)
stats = bt.optimize(
    fast_ma=range(20, 100, 10),
    slow_ma=range(30, 120, 10),
    maximize='Return [%]'
)
```

## 실제 거래 연동 (고급)

Binance API 예시:
```python
from binance.client import Client

# API 키 설정
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_SECRET'
client = Client(api_key, api_secret)

# 실시간 가격 확인
price = client.get_symbol_ticker(symbol="BTCUSDT")

# 주문 (테스트넷에서만!)
order = client.create_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=0.001
)
```

**⚠️ 주의**: 실제 거래는 리스크가 큽니다. 충분한 테스트 후 소액으로 시작하세요!

## 학습 자료

- [backtesting.py 공식 문서](https://kernc.github.io/backtesting.py/)
- [yfinance 문서](https://pypi.org/project/yfinance/)
- [Pandas 튜토리얼](https://pandas.pydata.org/docs/user_guide/index.html)

## 트러블슈팅

### 데이터 다운로드 실패
```bash
# yfinance 최신 버전으로 업데이트
pip install --upgrade yfinance
```

### 차트가 안 보임
```python
# matplotlib 백엔드 설정
import matplotlib
matplotlib.use('TkAgg')  # 또는 'Qt5Agg'
```

### TA-Lib 설치 오류 (Mac)
```bash
brew install ta-lib
pip install ta-lib
```

---

**다음 단계**: 백테스트 결과를 확인하고 전략을 개선하세요!
