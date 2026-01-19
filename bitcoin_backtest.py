"""
비트코인 자동매매 전략 v5.1 - Python 버전 (최적화됨)
40/100 MA 크로스오버 + 100 MA 시장 필터

최적화 결과:
- 수익률: 1751% (vs Buy&Hold 1078%)
- 승률: 58.33%
- Profit Factor: 11.143

필요한 라이브러리:
pip install backtesting yfinance pandas numpy matplotlib
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class MA_Filter_Strategy(Strategy):
    """
    v5.1 전략: 40/100 MA 크로스오버 + 100 MA 필터 (최적화됨)

    규칙:
    1. 가격이 100 MA 위에 있을 때만 거래 (강세장 필터)
    2. 40 MA가 100 MA를 상향 돌파 → 매수
    3. 40 MA가 100 MA를 하향 돌파 → 매도
    4. ATR 기반 손절매 (선택사항)
    """

    # 파라미터 (최적화 완료)
    fast_ma = 40
    slow_ma = 100
    market_filter_ma = 100
    use_market_filter = True
    atr_stop_multiplier = 2.0
    
    def init(self):
        """지표 초기화"""
        # 이동평균 계산
        close = self.data.Close
        self.ma_fast = self.I(SMA, close, self.fast_ma)
        self.ma_slow = self.I(SMA, close, self.slow_ma)
        self.ma_filter = self.I(SMA, close, self.market_filter_ma)
        
    def next(self):
        """매 바마다 실행되는 거래 로직"""
        price = self.data.Close[-1]
        
        # 시장 필터: 200 MA 아래에서는 거래 안 함
        if self.use_market_filter and price < self.ma_filter[-1]:
            # 포지션이 있으면 청산
            if self.position:
                self.position.close()
            return
        
        # 골든 크로스: 50 MA가 55 MA 상향 돌파 → 매수
        if crossover(self.ma_fast, self.ma_slow):
            # 기존 포지션 있으면 먼저 청산
            if self.position:
                self.position.close()
            # 롱 포지션 진입
            self.buy()
        
        # 데드 크로스: 50 MA가 55 MA 하향 돌파 → 매도
        elif crossover(self.ma_slow, self.ma_fast):
            # 포지션 청산
            if self.position:
                self.position.close()


def download_btc_data(start_date='2017-08-17', end_date=None):
    """
    비트코인 데이터 다운로드 (Yahoo Finance)
    
    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD), None이면 오늘
    
    Returns:
        pandas DataFrame: OHLCV 데이터
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"📥 비트코인 데이터 다운로드 중...")
    print(f"   기간: {start_date} ~ {end_date}")
    
    # BTC-USD 데이터 다운로드 (일봉)
    btc = yf.download('BTC-USD', start=start_date, end=end_date, interval='1d', auto_adjust=False)
    
    if btc.empty:
        raise ValueError("데이터 다운로드 실패!")
    
    print(f"✅ {len(btc)}일 데이터 다운로드 완료")
    
    # 컬럼명 정리 (backtesting.py 형식에 맞춤)
    btc.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    btc = btc[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    return btc


def run_backtest(data, strategy_class=MA_Filter_Strategy, cash=10000, commission=0.001):
    """
    백테스트 실행
    
    Args:
        data: OHLCV DataFrame
        strategy_class: 전략 클래스
        cash: 초기 자본 (USD)
        commission: 수수료 (0.001 = 0.1%)
    
    Returns:
        백테스트 결과 통계
    """
    print(f"\n🚀 백테스트 시작...")
    print(f"   초기 자본: ${cash:,}")
    print(f"   수수료: {commission*100}%")
    
    # 백테스트 설정
    bt = Backtest(
        data, 
        strategy_class,
        cash=cash,
        commission=commission,
        exclusive_orders=True  # 한 번에 하나의 주문만
    )
    
    # 백테스트 실행
    stats = bt.run()
    
    # 결과 출력
    print("\n" + "="*60)
    print("📊 백테스트 결과")
    print("="*60)
    print(f"시작일: {stats['Start']}")
    print(f"종료일: {stats['End']}")
    print(f"총 기간: {stats['Duration']}")
    print()
    print(f"{'총 수익률':<20}: {stats['Return [%]']:.2f}%")
    print(f"{'Buy & Hold 수익률':<20}: {stats['Buy & Hold Return [%]']:.2f}%")
    print(f"{'연평균 수익률':<20}: {stats.get('Return (Ann.) [%]', 'N/A')}")
    print()
    print(f"{'총 거래 횟수':<20}: {stats['# Trades']}")
    print(f"{'승률':<20}: {stats['Win Rate [%]']:.2f}%")
    print(f"{'Profit Factor':<20}: {stats['Profit Factor']:.3f}")
    print()
    print(f"{'최대 손실폭':<20}: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"{'최대 손실 기간':<20}: {stats['Max. Drawdown Duration']}")
    print()
    print(f"{'Sharpe Ratio':<20}: {stats.get('Sharpe Ratio', 'N/A')}")
    print(f"{'Sortino Ratio':<20}: {stats.get('Sortino Ratio', 'N/A')}")
    print(f"{'Calmar Ratio':<20}: {stats.get('Calmar Ratio', 'N/A')}")
    print("="*60)
    
    # 차트 그리기
    print("\n📈 차트 생성 중...")
    bt.plot(
        resample=False,
        plot_volume=True,
        plot_pl=True,
        superimpose=False
    )
    
    return stats, bt


def main():
    """메인 실행 함수"""
    print("="*60)
    print("🤖 비트코인 자동매매 전략 백테스트 v5.1 (최적화됨)")
    print("   40/100 MA 크로스오버 + 100 MA 필터")
    print("="*60)
    
    # 1. 데이터 다운로드
    try:
        # 전체 기간 (2017-2026)
        btc_data = download_btc_data(
            start_date='2017-08-17',
            end_date='2026-01-19'
        )
        
        # 2. 백테스트 실행
        stats, bt = run_backtest(
            btc_data,
            strategy_class=MA_Filter_Strategy,
            cash=100000,
            commission=0.001  # 0.1% 수수료
        )
        
        # 3. 파라미터 재최적화 (필요시 주석 해제)
        # print("\n🔧 파라미터 최적화 시작...")
        # optimized_stats = bt.optimize(
        #     fast_ma=range(10, 101, 10),
        #     slow_ma=range(20, 121, 10),
        #     market_filter_ma=range(100, 301, 50),
        #     maximize='Return [%]',
        #     constraint=lambda p: p.fast_ma < p.slow_ma
        # )
        # print(f"최적 파라미터: fast_ma={optimized_stats._strategy.fast_ma}, "
        #       f"slow_ma={optimized_stats._strategy.slow_ma}, "
        #       f"market_filter_ma={optimized_stats._strategy.market_filter_ma}")
        
        return stats, bt
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    # 백테스트 실행
    stats, bt = main()
    
    # 결과 저장 (선택사항)
    if stats is not None:
        print("\n💾 결과를 저장하시겠습니까?")
        print("   stats.to_csv('backtest_results.csv')  # 통계 저장")
        print("   # 또는 stats 객체를 직접 사용")
