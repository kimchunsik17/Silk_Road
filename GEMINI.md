프로젝트 목표: '바이브코딩' 요구사항에 명시된 깨끗한 도메인 모델, 책임 분리, 테스트 용이성, 효율적인 데이터 처리 원칙을 준수하는 확장 가능한 카라반 공유 플랫폼 MVP를 구축합니다.

핵심 기술 스택:

Backend: Python, Django

Database: SQLite (개발용), PostgreSQL (배포 고려)

Testing: pytest-django

🚀 Phase 1: 프로젝트 설정 및 핵심 도메인 모델링 (과제 1)
목표: Django 프로젝트를 설정하고, 과제 1의 요구사항에 맞는 깨끗하고 응집도 높은 도메인 모델(models.py)을 설계합니다.

Django 프로젝트/앱 설정

프로젝트 생성: django-admin startproject config .

앱 생성: python manage.py startapp core (핵심 비즈니스 로직)

core 앱 내에 models/, services/, repositories/, exceptions/ 디렉토리 구조 생성 (과제 요구사항 반영)

core/models/ 모델 설계 (SRP 준수)

models/user.py: User (Custom)

Django의 AbstractUser를 상속받아 User 모델을 확장합니다.

UserType (Choice Field: HOST, GUEST) 필드 추가.

프로필 정보 (연락처, 신원 확인 여부 is_verified) 추가.

models/caravan.py: Caravan

host (FK to User): 카라반 소유자 (공급자).

name, description, capacity (수용 인원), amenities (편의시설, M2M 또는 JSONField), location.

status (Choice Field: AVAILABLE, RESERVED, MAINTENANCE).

models/reservation.py: Reservation

guest (FK to User): 예약자 (수요자).

caravan (FK to Caravan): 예약된 카라반.

start_date, end_date.

status (Choice Field: PENDING, CONFIRMED, CANCELLED).

models/payment.py: Payment

reservation (FK to Reservation): 결제 대상 예약.

amount, status (Choice Field: PAID, FAILED).

paid_at (결제 완료 시간).

models/review.py: Review

reservation (FK to Reservation): 리뷰 대상 거래.

reviewer (FK to User): 리뷰 작성자.

target_user (FK to User): 리뷰 대상자 (호스트 또는 게스트).

rating (Integer, 1-5점), comment.

🚀 Phase 2: 리포지토리 및 서비스 로직 분리 (과제 2, 3, 7)
목표: '나쁜 설계 예시'에서 보인 비효율적인 O(n) 검색과 로직 결합 문제를 해결합니다. Django ORM을 활용한 리포지토리 패턴과 비즈니스 로직을 담당하는 서비스 레이어를 구현합니다.

core/repositories/ 설계 (과제 3: 효율적 검색)

목적: 데이터베이스 접근 로직을 캡슐화합니다. Django의 Manager/QuerySet을 활용합니다.

CaravanRepository:

get_by_id(id): O(1) 검색.

find_available(start_date, end_date, capacity): 예약 가능한 카라반 검색 (날짜 충돌 제외).

ReservationRepository:

check_conflict(caravan_id, start_date, end_date): 중복 예약 검사 최적화 (핵심). Django의 Q 객체와 __overlap (PostgreSQL) 또는 __range 조회를 사용하여 DB 레벨에서 효율적으로 검사합니다.

core/services/validators.py 설계 (과제 2: 비즈니스 로직 분리)

목적: 복잡한 '예약 검증' 로직을 별도 클래스로 분리하여 테스트 용이성을 확보합니다.

ReservationValidator:

def __init__(self, reservation_repo: ReservationRepository): 의존성 주입 (DI).

def validate(self, user, caravan, start_date, end_date): 메인 검증 메서드.

def _is_date_available(self, caravan, start_date, end_date): (private) 날짜 중복 검사 (리포지토리 호출).

def _can_user_book(self, user): (private) 게스트 자격 검사.

def _is_caravan_available(self, caravan): (private) 카라반 상태 검사.

core/services/reservation_service.py 설계 (과제 7: 팩토리 패턴)

목적: 예약 생성/승인/거절 등 핵심 비즈니스 로직을 처리합니다.

ReservationService:

def __init__(self, validator: ReservationValidator, payment_service, notification_service): DI.

def create_reservation(self, user_id, caravan_id, start_date, end_date):

validator.validate(...) 호출 (실패 시 예외 발생).

가격 계산 ( 전략 패턴 적용: StandardPricingStrategy 주입).

PaymentService.request_payment(...) 호출.

Reservation 객체 생성 ( 팩토리 패턴 활용).

NotificationService.notify(...) 호출 ( 옵저버 패턴: Django Signals로 구현).

🚀 Phase 3: API/View 및 예외 처리 (과제 4, 5)
목표: 엔드포인트(View)를 구현하고, 명확한 네이밍 및 견고한 예외 처리 전략을 수립합니다.

core/views.py 또는 API 구현

Django View 또는 DRF(Django REST Framework)를 사용하여 각 기능의 엔드포인트를 구현합니다.

네이밍 (과제 4):

Views/Functions: create_reservation, get_caravan_details.

Boolean: is_available, has_permission.

core/exceptions.py 설계 (과제 5: 커스텀 예외)

목적: 도메인 특화 예외를 정의하여 명확한 에러 처리를 합니다.

class ReservationConflictError(Exception): 중복 예약 시 발생.

class PaymentFailedError(Exception): 결제 실패 시 발생.

class InsufficientPermissionsError(PermissionError): 권한 부족 시 발생.

View에서의 예외 처리

services 계층에서 발생한 커스텀 예외(ReservationConflictError 등)를 views에서 try-except로 잡아 사용자에게 명확한 에러 메시지(예: 400 Bad Request)를 반환합니다.

🚀 Phase 4: 테스트 및 배포 (과제 6)
목표: 의존성 주입(DI) 구조를 활용하여 단위 테스트를 작성하고, 테스트 커버리지 70% 이상을 달성합니다.

tests/ 디렉토리 구성

tests/test_models.py: 모델 생성 및 기본 로직 테스트.

tests/test_repositories.py: DB 쿼리(특히 날짜 충돌) 로직 집중 테스트.

tests/test_validators.py: (핵심) ReservationValidator 집중 테스트. Mock 리포지토리를 주입하여 다양한 시나리오(성공, 날짜 중복, 권한 없음)를 검증합니다.

tests/test_services.py: ReservationService가 올바른 순서로 validator, payment 등을 호출하는지 Mock을 활용해 테스트.

테스트 커버리지 측정

pytest --cov=core 명령어로 커버리지 70% 달성 확인.

📂 최종 프로젝트 구조 (제출 형식)
your_project/
├── config/                 # Django 프로젝트 설정 (settings.py, urls.py)
├── core/                   # 핵심 비즈니스 로직 앱
│   ├── migrations/
│   ├── models/             # (Phase 1)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── caravan.py
│   │   ├── reservation.py
│   │   └── ... (payment.py, review.py)
│   ├── services/             # (Phase 2)
│   │   ├── __init__.py
│   │   ├── reservation_service.py
│   │   ├── payment_service.py
│   │   └── validators.py     # (ReservationValidator)
│   ├── repositories/         # (Phase 2)
│   │   ├── __init__.py
│   │   ├── reservation_repository.py
│   │   └── caravan_repository.py
│   ├── exceptions/           # (Phase 3)
│   │   └── __init__.py
│   ├── views.py              # (Phase 3)
│   ├── admin.py
│   └── apps.py
├── tests/                  # (Phase 4)
│   ├── test_models.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_validators.py
├── manage.py
├── README.md               # 프로젝트 설명
├── DESIGN.md               # 설계 결정 (본 GEMINI.md 내용 기반으로 작성)
└── requirements.txt