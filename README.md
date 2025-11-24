#  Silk Road  caravan
카라반(캠핑카)을 소유한 사람(호스트)과 이용하고 싶은 사람(게스트)을 연결하는 카라반 공유 플랫폼입니다.

live demo : https://34.64.46.126/

## 🌟 주요 기능

- **사용자 관리:** 회원가입, 로그인 및 소셜 로그인(Google) 기능. 호스트와 게스트 역할 분리.
- **카라반 목록 및 상세 정보:** 호스트는 자신의 카라반을 등록하고, 사진, 설명, 편의시설 등 상세 정보를 관리할 수 있습니다.
- **예약 시스템:** 게스트는 원하는 날짜에 카라반을 예약하고, 호스트는 예약을 수락/거절할 수 있습니다.
- **결제 기능:** 예약 시 결제 기능을 연동하여 안전한 거래를 보장합니다.
- **리뷰 및 평점:** 사용자는 거래가 완료된 다른 사용자에 대해 리뷰와 평점을 남길 수 있습니다.
- **실시간 채팅:** 사용자는 예약 과정에서 서로 실시간으로 소통할 수 있습니다.
- **관리자 페이지:** 관리자는 모든 데이터(사용자, 카라반, 예약 등)를 웹 인터페이스에서 손쉽게 관리할 수 있습니다.

## 🛠️ 기술 스택

- **Backend:** Python, Django, Django REST Framework
- **Database:** SQLite3 (개발용), PostgreSQL (배포용)
- **Frontend:** HTML, CSS, JavaScript
- **CI/CD:** GitHub Actions
- **Libraries:**
  - `django-allauth` for social login
  - `Pillow` for image handling
  - `pytest-django` for testing

## 🚀 시작하기

### 1. 프로젝트 복제
```bash
git clone https://github.com/your-username/Silk_Road.git
cd Silk_Road
```

### 2. 가상환경 설정 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 설정
```bash
python manage.py migrate
```

### 5. 관리자 계정 생성
```bash
python manage.py createsuperuser
```
안내에 따라 관리자 아이디, 이메일, 비밀번호를 설정합니다.

### 6. 개발 서버 실행
```bash
python manage.py runserver
```
서버가 실행되면 웹 브라우저에서 `http://127.0.0.1:8000` 로 접속하여 확인할 수 있습니다.

## ⚙️ 관리자 페이지

관리자는 `http://127.0.0.1:8000/admin` 경로로 접속하여 위에서 생성한 관리자 계정으로 로그인할 수 있습니다.

관리자 페이지에서는 다음을 포함한 모든 데이터를 관리할 수 있습니다.
- 사용자 정보 및 권한 관리
- 카라반 정보 수정 및 상태 변경
- 예약 내역 확인 및 관리
- 리뷰, 결제, 채팅 등 모든 기록 조회

## 🔄 자동 배포 (CI/CD)

이 프로젝트는 GitHub Actions를 사용하여 `main` 또는 `master` 브랜치에 코드가 푸시될 때 서버에 자동으로 배포됩니다. 배포 과정은 다음을 포함합니다:

1. 최신 코드 다운로드 (`git pull`)
2. 라이브러리 업데이트 (`pip install -r requirements.txt`)
3. 데이터베이스 마이그레이션 (`migrate`) 및 정적 파일 수집 (`collectstatic`)
4. 서버 재시작

자세한 내용은 `.github/workflows/deploy.yml` 파일을 참고하세요.
