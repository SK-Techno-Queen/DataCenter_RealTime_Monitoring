# DataCenter_RealTime_Monitoring

## 설치해야 할 패키지

다음 명령어로 필요한 패키지들을 설치하세요:

```
pip install Flask psycopg2-binary Flask-Cors
```

### 각 패키지 설명
- **Flask**: 웹 애플리케이션을 개발하기 위한 경량 프레임워크입니다.
- **psycopg2-binary**: PostgreSQL 데이터베이스와 연결하기 위한 Python 어댑터입니다.
- **Flask-Cors**: Flask 애플리케이션에 CORS (Cross-Origin Resource Sharing) 정책을 적용하는 데 사용되는 모듈입니다.



<br>

## 파일 구조
1. app.py -> flask 기반 백엔드 코드
2. templates -> html 코드
3. static -> css 코드
4. logdata_generate.py -> 로그 데이터 생성 코드
