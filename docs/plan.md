# Gemini-Claw 프로젝트 계획

## 1. 개요
이 프로젝트는 **Gemini CLI**와 **uv**를 기반으로 작동하는 로컬 AI 에이전트 **Gemini-Claw**를 구축하는 것을 목표로 합니다.
1차 목표는 `uv run` 명령어로 실행하며, 최신 AI 뉴스(DeepMind, OpenAI)를 검색하고 분석하여 URL과 함께 리포트를 제공하는 에이전트를 만드는 것입니다.
최종 목표는 스스로 코드를 수정하고 개선하는 AGI 수준의 자가 발전형 에이전트로 진화하는 것입니다.

## 2. 기술 스택
- **Language**: Python 3.12+
- **Package Manager**: `uv` (빠르고 효율적인 패키지 관리)
- **Core Engine**: `gemini-cli` (Google Gemini 3 모델 활용)
- **Interface**: CLI (Command Line Interface), Headless Mode 활용

## 3. 파일 구조
```
gemini-claw/
├── docs/
│   ├── plan.md           # 본 계획서
│   └── architecture.md   # 상세 아키텍처 (추후 작성)
├── src/
│   ├── main.py           # 진입점 (Entry Point)
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py       # gemini-cli 래퍼 클래스
│   │   ├── tools.py      # 추가 도구 (필요 시)
│   │   └── utils.py      # 유틸리티 함수
├── pyproject.toml        # uv 프로젝트 설정
└── README.md
```

## 4. 구현 상세 계획

### 1단계: 환경 설정 및 기본 구조 잡기
- `uv init`을 통해 프로젝트 초기화.
- 필요한 Python 패키지 의존성 정의.
- `gemini-cli`가 시스템에 설치되어 있는지, 환경 변수 설정이 올바른지 확인하는 로직 포함.

### 2단계: Gemini CLI 연동 (Headless Mode)
- `src/agent/core.py`에서 `subprocess`를 사용하여 `gemini-cli`를 호출.
- `--model gemini-3-flash-preview` (또는 최신 3 버전) 플래그 사용.
- JSON Output Format(`--output-format json`)을 사용하여 프로그램이 응답을 파싱할 수 있도록 구현.

### 3단계: 뉴스 검색 기능 구현
- `gemini-cli`의 내장 `google_web_search` 도구를 적극 활용.
- 사용자가 입력한 쿼리를 효과적인 프롬프트로 변환하여 `gemini-cli`에 전달.
- 예: "DeepMind와 OpenAI의 최신 동향을 검색하고, 거품론에 대한 분석과 함께 관련 기사 URL을 나열해줘."

### 4단계: 실행 인터페이스
- `uv run python -m src.main --query "..."` 형태로 실행 가능하도록 `argparse` 또는 `click` 사용.

## 5. 실행 예시
```bash
uv run python -m src.main --query "딥마인드와 openai의 최신 뉴스들을 검색해서 인공지능 업계의 동향을 알려줘..."
```

## 6. 최종 목표 (Self-Improvement) 향한 로드맵
- **Reflection**: 에이전트가 자신의 수행 결과를 평가하는 모듈 추가.
- **Self-Modification**: 에이전트가 `src` 코드를 직접 읽고 수정할 수 있는 `File Editor` 도구 권한 부여.
- **Workflow Loop**: 계획 -> 실행 -> 평가 -> 개선의 무한 루프 구축.

이 계획에 따라 프로젝트를 진행하며, 단계별로 기능을 검증하겠습니다.
