#!/bin/bash
# ============================================================================
# 서버 초기 설정 스크립트
# Oracle Cloud Ubuntu 22.04 기준
# ============================================================================

set -e  # 에러 발생 시 중단

echo "=========================================="
echo "🚀 비트코인 자동매매 봇 서버 설정 시작"
echo "=========================================="

# 1. 시스템 업데이트
echo ""
echo "📦 1/6. 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 2. Python 및 필수 패키지 설치
echo ""
echo "🐍 2/6. Python 설치 중..."
sudo apt install -y python3 python3-pip python3-venv git

# 3. 프로젝트 디렉토리 생성
echo ""
echo "📁 3/6. 프로젝트 디렉토리 생성..."
mkdir -p ~/trading-bot
cd ~/trading-bot

# 4. GitHub에서 코드 클론 (URL 변경 필요)
echo ""
echo "📥 4/6. 코드 다운로드..."
# git clone https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git .
echo "⚠️  GitHub URL을 설정한 후 아래 명령어 실행:"
echo "    git clone https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git ."

# 5. 가상환경 생성 및 패키지 설치
echo ""
echo "📚 5/6. Python 가상환경 설정..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_trading.txt

# 6. 환경변수 파일 생성
echo ""
echo "🔐 6/6. 환경변수 파일 생성..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  .env 파일을 편집하여 API 키를 입력하세요:"
    echo "    nano .env"
fi

echo ""
echo "=========================================="
echo "✅ 서버 설정 완료!"
echo "=========================================="
echo ""
echo "📋 다음 단계:"
echo "   1. .env 파일에 API 키 입력: nano .env"
echo "   2. 테스트 실행: python3 bithumb_trading_bot.py"
echo "   3. systemd 서비스 등록: sudo ./install_service.sh"
echo ""
