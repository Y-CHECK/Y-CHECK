## 🔐 Y-CHECK

“Y-CHECK”은 연세대학교 미래캠퍼스 학생들을 위한 졸업요건 계산, 시간표 관리, 선배 시간표 공유 기능을 제공하는 통합 웹 플랫폼입니다.
본 서비스는 외부망(Web Server), 내부망(API Server), DB Server(PostgreSQL) 로 구성된 3계층 보안 구조를 차용하여 설계되었으며, 특히 외부망에서는 HTML 기반 UI만 제공하고 내부망에서 실제 로직과 데이터 처리가 이루어지는 DMZ(비무장지대) 아키텍처를 구현하고 있습니다.

Y-CHECK을 통해 사용자는 시간표 생성 및 공유, 졸업요건 자동 계산, 사용자 정보 관리 등의 기능을 안전하게 수행하게 되며 개발자는 웹 분리 구조, API 인증/인가 처리, DB 연동, 컨테이너 기반 서비스 운영까지 실제 서비스 운영 환경에 준하는 개발 경험을 할 수 있습니다.
web → api → db 로 흐르는 단방향 보안 구조를 실습할 수 있으며, 과목 DB 로딩, 시간표 저장 로직, 내부망 보호를 위한 네트워크 분리 등 실전형 개발 구조를 학습하는 데 도움이 됩니다.


---

## 🛠️ Technology Stack
<img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white&style=for-the-badge"/> <img src="https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white&style=for-the-badge"/> <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge"/>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge"/>
<img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge"/> <img src="https://img.shields.io/badge/Docker_Compose-2496ED?logo=docker&logoColor=white&style=for-the-badge"/> <img src="https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white&style=for-the-badge"/>
---

## 📑 목차
1. 사용 방법
2. 네트워크 구상도
3. 기여자
4. 협업 방식
5. 개발 기간
---

## 사용 방법
```
# 전체 서비스 시작
docker-compose up -d --build

# 전체 서비스 중지
docker-compose down

# 회원가입 & 로그인 
docker compose down -v
docker compose up -d --build
docker compose logs db --tail=50
docker compose restart api web
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
docker compose exec api python manage.py makemigrations users
docker compose exec api python manage.py migrate

# 계산기에 사용되는 과목 DB에 삽입
docker compose exec api python manage.py makemigrations //최초 1회만 진행
docker compose exec api python manage.py migrate
docker compose exec api python manage.py load_courses /app/courses.json

# 시간표에 사용되는 과목 DB에 삽입
docker compose exec api python manage.py makemigrations //최초 1회만 진행
docker compose exec api python manage.py migrate
docker compose exec api python manage.py loaddata /app/timetable_courses.json

```
# 네트워크 구상도
<img width="1168" height="321" alt="Image" src="https://github.com/user-attachments/assets/b705f71b-1bc5-4db9-a78c-109dccaf5731" />
---


## 👏 기여자 표

<h3>Project Team</h3>

<table>
  <thead>
    <tr>
      <th>Profile</th>
      <th>Role</th>
      <th>Expertise</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/Ranunculus2165">
          <img src="https://github.com/Ranunculus2165.png" width="60"/><br/>
          woo.__.bee
        </a>
      </td>
      <td align="center">Project Manager</td>
      <td align="center">기본 구조 생성, 백엔드 API, DB</td>
    </tr>
     </tbody>
  <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/xo0102">
          <img src="https://github.com/xo0102.png" width="60"/><br/>
          xo0102
        </a>
      </td>
      <td align="center">Project Member</td>
      <td align="center">백엔드 API</td>
    </tr>
     </tbody>
  <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/kietma513">
          <img src="https://github.com/kietma513.png" width="60"/><br/>
          kietma513
        </a>
      </td>
      <td align="center">Project Member</td>
      <td align="center">백엔드 API</td>
    </tr>
     </tbody>
   <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/Bloxxom22">
          <img src="https://github.com/Bloxxom22.png" width="60"/><br/>
          Bloxxom22
        </a>
      </td>
      <td align="center">Project Member</td>
      <td align="center">프론트엔드</td>
    </tr>
     </tbody>
  <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/JayHLee8">
          <img src="https://github.com/JayHLee8.png" width="60"/><br/>
          JaeHoon Lee
        </a>
      </td>
      <td align="center">Project Member</td>
      <td align="center">프론트엔드</td>
    </tr>
     </tbody>
</table>

---

## 🔥 협업 방식

| 🖥️ 플랫폼 | 🛠️ 사용 방식 |
|-----------|--------------|
| ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white) | 매주 목요일,토요일 2시 회의 |
| ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white) | PR을 통해 변경사항 및 테스트 과정 확인 |
| ![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white) | 시나리오 구성, API, 회의 기록 문서화 |

---

## 📆 개발 기간

- 2025.10.11 ~ 2025.10.15 : 아이디어 회의
- 2025.10.15 ~ 2025.10.22 : 최종 아이디어 선정
- 2025.10.22 ~ 2025.10.30 : API 명세서 작성
- 2025.11.01 ~ 2025.11.10 : 와이어프레임 작성
- 2025.11.11 ~ 2025.11.13 : 기본 구조 생성 및 DB 연결
- 2025.11.14 ~ 2025.11.29 : 프론트엔드 및 백엔드 연동

---

