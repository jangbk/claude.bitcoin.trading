#!/bin/bash
# ============================================================================
# systemd 서비스 설치 스크립트
# 24시간 365일 자동 실행 설정
# ============================================================================

set -e

echo "=========================================="
echo "🔧 systemd 서비스 설치"
echo "=========================================="

# 서비스 파일 복사
echo "📋 서비스 파일 복사 중..."
sudo cp trading-bot.service /etc/systemd/system/

# systemd 리로드
echo "🔄 systemd 리로드..."
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
echo "✅ 서비스 활성화..."
sudo systemctl enable trading-bot

# 서비스 시작
echo "🚀 서비스 시작..."
sudo systemctl start trading-bot

# 상태 확인
echo ""
echo "=========================================="
echo "📊 서비스 상태"
echo "=========================================="
sudo systemctl status trading-bot --no-pager

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "📋 유용한 명령어:"
echo "   상태 확인:  sudo systemctl status trading-bot"
echo "   로그 보기:  journalctl -u trading-bot -f"
echo "   재시작:     sudo systemctl restart trading-bot"
echo "   중지:       sudo systemctl stop trading-bot"
echo "   비활성화:   sudo systemctl disable trading-bot"
echo ""
