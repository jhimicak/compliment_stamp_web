# 무료 배포 가이드 (Render)

이 프로젝트는 [Render](https://render.com/)를 통해 **무료로 배포**할 수 있도록 기본 설정(`render.yaml`, `wsgi.py`, `requirements.txt`)이 준비되어 있습니다.

Render는 코드를 GitHub에 올리기만 하면 자동으로 웹서비스를 실행해주는 클라우드 플랫폼입니다.

## 배포 순서

### 1. GitHub에 코드 올리기
먼저 작성된 코드를 본인의 GitHub 계정에 새로운 Repository를 만들어 업로드합니다.

### 2. Render 회원가입 및 연동
1. [Render](https://render.com/)에 접속하여 GitHub 계정으로 로그인 (가입) 합니다.
2. 대시보드에서 **[New] -> [Web Service]**를 클릭합니다.
3. `Build and deploy from a Git repository`를 선택하고, 방금 만든 본인의 GitHub Repository를 검색하여 연결(Connect)합니다.

### 3. 프로젝트 설정
GitHub 저장소를 연결하면 환경 설정 화면이 나오는데, 이미 `render.yaml` 파일이 있기 때문에 대부분 자동으로 인식됩니다.
수동으로 설정해야 한다면 아래와 같이 입력합니다.

* **Name**: 서비스 이름 입력 (예: `compliment-stamp`)
* **Region**: `Singapore` (가장 가까운 곳)
* **Branch**: `main` (또는 코드가 있는 브랜치)
* **Runtime**: `Python 3`
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `gunicorn wsgi:app`

설정을 완료하고 아래쪽의 **[Create Web Service]** 버튼을 누르면 배포가 시작됩니다!

---

### 배포 후 데이터베이스 관련 주의사항
무료 클라우드 환경에서는 일정 시간 사용하지 않으면 서버가 잠들(Sleep) 수 있고, 재시작될 때 파일이 초기화될 수 있습니다. 
따라서 실제 서비스 운영 시에는 SQLite 파일(`database.db`) 대신, Render에서 제공하는 **무료 PostgreSQL 호스팅**을 추가로 생성하여 연결하는 것이 좋습니다.

#### (선택 사항) PostgreSQL 연결 방법
1. Render 대시보드에서 **[New] -> [PostgreSQL]**을 선택해 무료 DB를 만듭니다.
2. 생성된 DB의 `Internal Database URL` 값을 복사합니다.
3. 웹 서비스(Web Service) 환경 변수(Environment Variables) 설정에서 `DATABASE_URL`이라는 이름으로 복사한 URL을 넣습니다.
4. `app.py` 소스 코드의 `app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')` 처럼 수정하면 외부 DB를 안전하게 사용할 수 있습니다.
