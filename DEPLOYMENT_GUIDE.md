# 🚀 24시간 자동매매 서버 배포 가이드

## 📋 전체 흐름도

```
[로컬 PC] → [GitHub] → [클라우드 서버] → [24시간 실행]
                              ↓
                       [텔레그램 알림]
```

---

## 1️⃣ 사전 준비

### 필요한 것
- [ ] 빗썸 계정 및 API 키
- [ ] GitHub 계정
- [ ] Oracle Cloud 계정 (무료)
- [ ] 텔레그램 계정 (알림용, 선택)

---

## 2️⃣ GitHub 업로드

### 2-1. GitHub에서 새 저장소 생성
1. github.com 접속 → 로그인
2. "New repository" 클릭
3. Repository name: `bitcoin-trading-bot`
4. **Private** 선택 (중요! 코드 비공개)
5. "Create repository" 클릭

### 2-2. 로컬에서 업로드
```bash
cd "Bitcoin Autotrading_Trading View_Pine Script"

# Git 초기화 (이미 완료됨)
git add .
git commit -m "Initial commit: BTC trading bot v5.1"

# GitHub 연결
git remote add origin https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git
git branch -M main
git push -u origin main
```

---

## 3️⃣ Oracle Cloud 서버 생성

### 3-1. 계정 생성
1. https://cloud.oracle.com 접속
2. "Start for free" 클릭
3. 정보 입력 (신용카드 필요, 과금 없음)

### 3-2. VM 인스턴스 생성
```
1. Console → Compute → Instances
2. "Create Instance" 클릭
3. 설정:
   - Name: trading-bot
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (무료!)
     - OCPU: 1
     - Memory: 6GB
   - Add SSH keys: 공개키 붙여넣기
4. "Create" 클릭
```

### 3-3. 방화벽 설정
```
1. Networking → Virtual Cloud Networks
2. VCN 선택 → Security Lists
3. Ingress Rules 추가:
   - SSH (22): 본인 IP만 허용 권장
```

---

## 4️⃣ 서버 접속 및 설정

### 4-1. SSH 접속
```bash
ssh -i ~/.ssh/id_rsa ubuntu@YOUR_SERVER_IP
```

### 4-2. 초기 설정
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install -y python3 python3-pip python3-venv git

# 프로젝트 폴더 생성
mkdir -p ~/trading-bot
cd ~/trading-bot

# GitHub에서 코드 다운로드
git clone https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git .

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements_trading.txt
```

### 4-3. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env
nano .env
```

**.env 파일 내용:**
```
BITHUMB_API_KEY=실제_API_키
BITHUMB_API_SECRET=실제_시크릿_키
TELEGRAM_TOKEN=텔레그램_봇_토큰
TELEGRAM_CHAT_ID=본인_챗_ID
```

### 4-4. 테스트 실행
```bash
source venv/bin/activate
python3 bithumb_trading_bot.py
```

---

## 5️⃣ 24시간 자동 실행 설정

### 5-1. systemd 서비스 등록
```bash
# 서비스 파일 복사
sudo cp trading-bot.service /etc/systemd/system/

# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

### 5-2. 상태 확인
```bash
# 서비스 상태
sudo systemctl status trading-bot

# 실시간 로그
journalctl -u trading-bot -f

# 최근 로그 100줄
journalctl -u trading-bot -n 100
```

---

## 6️⃣ 유용한 명령어

### 서비스 관리
```bash
# 시작
sudo systemctl start trading-bot

# 중지
sudo systemctl stop trading-bot

# 재시작
sudo systemctl restart trading-bot

# 비활성화 (부팅 시 자동 시작 안 함)
sudo systemctl disable trading-bot
```

### 로그 확인
```bash
# systemd 로그
journalctl -u trading-bot -f

# 봇 로그 파일
tail -f ~/trading-bot/trading_bot.log
```

### 코드 업데이트
```bash
cd ~/trading-bot
git pull origin main
sudo systemctl restart trading-bot
```

---

## 7️⃣ 보안 체크리스트

### 필수
- [ ] API 출금 권한 **비활성화**
- [ ] .env 파일 GitHub에 **절대 업로드 금지**
- [ ] SSH 키 방식 접속 사용
- [ ] 서버 방화벽 설정

### 권장
- [ ] SSH 포트 변경 (22 → 다른 포트)
- [ ] fail2ban 설치 (무차별 접속 차단)
- [ ] 정기적 보안 업데이트

```bash
# fail2ban 설치
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

---

## 8️⃣ 문제 해결

### 봇이 실행되지 않을 때
```bash
# 로그 확인
journalctl -u trading-bot -n 50

# 수동 실행 테스트
cd ~/trading-bot
source venv/bin/activate
python3 bithumb_trading_bot.py
```

### API 오류
- API 키 확인
- IP 화이트리스트 설정 확인
- 빗썸 서버 상태 확인

### 서버 재부팅 후 자동 시작 안 될 때
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

---

## 📱 텔레그램 봇 설정

### 1. 봇 생성
1. 텔레그램에서 @BotFather 검색
2. `/newbot` 입력
3. 봇 이름 입력
4. **토큰 저장**

### 2. Chat ID 확인
1. @userinfobot 검색
2. `/start` 입력
3. **ID 번호 저장**

### 3. 설정 적용
```python
# bithumb_trading_bot.py의 Config 클래스에서
TELEGRAM_ENABLED = True
TELEGRAM_TOKEN = "발급받은_토큰"
TELEGRAM_CHAT_ID = "본인_챗_ID"
```

---

## 💰 비용 요약

| 항목 | 비용 |
|------|------|
| Oracle Cloud 서버 | **무료** (평생) |
| GitHub Private | **무료** |
| 빗썸 거래 수수료 | 0.25% |
| 텔레그램 | **무료** |
| **총 비용** | **0원/월** |

---

## ⚠️ 주의사항

1. **투자 손실 책임**: 자동매매로 인한 손실은 전적으로 본인 책임
2. **소액 테스트**: 반드시 소액으로 충분히 테스트
3. **API 보안**: 출금 권한 비활성화 필수
4. **모니터링**: 정기적으로 봇 상태 확인
5. **백업**: .env 파일 안전하게 백업

---

**문서 버전**: 1.0
**최종 수정**: 2026-01-19
