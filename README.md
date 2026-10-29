# 급등주 진단 v4.0 · Stock Glass (Streamlit)

모바일과 PC에서 사용할 수 있는 반응형 glassmorphism 화면입니다. 분석 로직은 `stock_analysis_v4_0.py`의 `run_pipeline()`을 그대로 호출하며, 이 프로젝트는 화면과 실행 환경을 Streamlit으로 감싼 버전입니다.

## 로컬 실행

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 Streamlit이 출력하는 로컬 주소를 엽니다.

## GitHub + Streamlit Community Cloud 배포

1. GitHub에 새 저장소를 만듭니다(예: `stock-glass-v4`).
2. 이 폴더의 파일을 저장소 최상위에 업로드합니다. `app.py`, `stock_analysis_v4_0.py`, `requirements.txt`, `.streamlit/config.toml`, `README.md`가 필요합니다.
3. Streamlit Community Cloud에 로그인하고 **Create app**을 선택합니다.
4. GitHub 저장소, 브랜치(보통 `main`), 메인 파일 경로 `app.py`를 선택해 배포합니다.
5. 배포가 끝나면 생성된 웹 주소를 휴대폰과 PC에서 엽니다. 이후 GitHub에 코드를 반영하면 Streamlit이 다시 배포합니다.

## 중요한 사항

- 첫 실행은 가격 데이터 다운로드와 워크포워드 학습 때문에 시간이 걸릴 수 있습니다.
- 무료 호스팅 환경의 메모리·실행 시간 제한에 따라 일부 종목은 분석이 실패할 수 있습니다.
- 이 앱은 v4.0의 기존 계산 규칙을 유지하려는 UI 래퍼입니다. 모델의 투자 성과나 데이터 공급자의 가용성을 보장하지 않습니다.
- 미국 종목의 원화 환율 효과는 원본 v4.0과 같이 별도로 계산하지 않습니다.
- 앱을 공개 배포할 경우 종목 조회 화면은 누구나 열 수 있으므로, 개인 API 키나 비밀정보를 코드에 넣지 마세요.
