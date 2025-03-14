# README.md
# 네이버 플레이스 순위 검색 애플리케이션

네이버 플레이스에서 키워드 검색 시 특정 상호명의 순위를 추적하고 시각화하는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능

- **실시간 검색**: 키워드와 상호명을 입력하여 네이버 플레이스 순위 확인
- **자동 업데이트**: GitHub Actions를 통해 매일 오후 2시 자동 업데이트
- **데이터 시각화**: 시간에 따른 순위 변화 차트 및 게이지 차트
- **업체 관리**: 여러 업체 정보 추가, 수정, 삭제
- **검색 기록**: 과거 검색 결과 조회 및 CSV 다운로드

## 설치 방법

### 로컬 설치

1. 저장소 클론
```bash
git clone https://github.com/your-username/naver-place-rank-tracker.git
cd naver-place-rank-tracker
```

2. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
streamlit run app.py
```

### Streamlit Cloud 배포

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에 로그인
3. "New app" 버튼 클릭
4. GitHub 저장소 연결 및 app.py 파일 지정
5. 배포 완료

## 사용 방법

1. **실시간 검색**
   - 검색어(예: 의정부 미용실)와 상호명(예: 준오헤어 의정부역점) 입력
   - 검색 버튼 클릭하여 순위 확인

2. **시각화 페이지**
   - 업체와 키워드 선택하여 시간에 따른 순위 변화 확인
   - 다양한 차트로 순위 추이 분석

3. **업체 관리**
   - 새 업체 추가 및 삭제
   - 등록된 업체 목록 확인

4. **검색 기록**
   - 과거 검색 결과 조회
   - 날짜별 필터링 및 CSV 다운로드

## 자동 업데이트 설정

GitHub Actions를 통해 매일 오후 2시에 자동으로 검색이 실행됩니다. 이를 위해서는:

1. GitHub 저장소에 코드 푸시
2. GitHub Actions 워크플로우 확인 (.github/workflows/daily_update.yml)
3. 필요시 워크플로우 수동 실행 가능

## 파일 구조

```
/
├── app.py                  # Streamlit 메인 애플리케이션
├── pages/                  # 멀티페이지 구성
│   ├── 01_visualization.py # 시각화 페이지
│   ├── 02_companies.py     # 업체 관리 페이지
│   └── 03_search_history.py # 검색 기록 페이지
├── modules/
│   ├── search_engine.py    # 네이버 플레이스 검색 엔진
│   └── data_manager.py     # 데이터 관리 모듈
├── scripts/
│   └── update_search_results.py # 자동 업데이트 스크립트
├── data/                   # 데이터 저장 디렉토리
│   ├── companies.csv       # 업체 정보
│   ├── keywords.csv        # 키워드 정보
│   └── search_results.csv  # 검색 결과 기록
├── .github/workflows/      # GitHub Actions 워크플로우
│   └── daily_update.yml    # 일일 업데이트 워크플로우
└── requirements.txt        # 의존성 패키지 목록
```

## 주의사항

- 네이버 서버에 과도한 부하를 주지 않도록 검색 간격 조절
- 웹 구조 변경 시 검색 엔진 업데이트 필요
- 자동 업데이트를 위해 GitHub 저장소 연결 필수
