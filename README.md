# 칭찬 스탬프 웹 서비스 (Compliment Stamp Web App)

![도장 이미지](static/images/stamp.png)

사용자들에게 칭찬 도장을 부여하고, 일정 개수를 모으면 쿠폰을 발급해주는 사내 이벤트용 웹 서비스입니다.

## 기능 소개

### 👨‍💼 관리자 권한
* **도장 찍기**: 사용자에게 칭찬 메시지와 함께 도장을 부여할 수 있습니다.
* **이벤트 설정**: 목표 도장 개수(기본 10개)를 설정하면, 도장을 목표 개수만큼 모은 사용자에게 자동으로 쿠폰이 발급됩니다.
* **수동 쿠폰 발급**: 이벤트 조건과 무관하게 관리자가 직접 사유를 입력하여 특별 쿠폰을 발급할 수도 있습니다.
* **현황 조회**: 모든 사용자의 도장 및 쿠폰 보유 현황을 통계로 한눈에 확인할 수 있습니다.

### 👤 사용자 권한
* **마이페이지(대시보드)**: 자신이 지금까지 받은 도장(과 칭찬 메시지) 및 획득한 쿠폰 내역을 언제든 확인할 수 있습니다.
* **쿠폰 획득**: 목표 도장 개수에 도달하면 자동으로 쿠폰이 들어옵니다.

## 기술 스택
* **Backend**: Python (Flask)
* **Database**: SQLite (SQLAlchemy)
* **Authentication**: Flask-Login, Werkzeug Security
* **Frontend**: HTML/CSS/JS + Jinja2 Templates (Bootstrap 또는 커스텀 CSS 사용 가능)
* **배포 친화적 환경**: `requirements.txt`와 `wsgi.py`, `render.yaml`를 통해 Render 등 무료 웹 호스팅 서비스로 쉽게 구동할 수 있습니다.

## 설치 및 실행 방법

1. **저장소 클론 및 폴더 이동**
   ```bash
   cd compliment_stamp_web
   ```

2. **가상환경 생성 및 활성화 (선택 사항)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **애플리케이션 실행**
   ```bash
   python app.py
   ```
   * *앱을 처음 실행시키면 `database.db` 파일이 자동 생성됩니다.*

## 기본 관리자 계정 정보
*앱 최초 구동 시 기본 관리자 계정이 자동으로 생성됩니다.*
* **아이디**: `admin`
* **비밀번호**: `admin123`
*(보안을 위해 로그인 후 데이터베이스나 코드에서 비밀번호를 변경하시는 것을 권장합니다.)*

## 디렉토리 구조
* `app.py`: 메인 앱 로직
* `models.py`: 데이터베이스 모델 (User, Stamp, Coupon, EventConfig)
* `static/images/stamp.png`: 도장 이미지 파일
* `templates/`: 화면 템플릿 파일들
* `database.db`: SQLite 데이터베이스 (앱 실행 시 자동 생성됨)