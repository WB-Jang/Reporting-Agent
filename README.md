# 대외기관 보고서 자동화 Agent

NiceGUI 기반 웹 인터페이스로 대외기관 보고서 자동화 에이전트를 손쉽게 사용할 수 있습니다.

---

## 주요 기능

| 기능 | 설명 |
|---|---|
| **보고서 실행** | 사이드바 버튼 클릭 → 채팅창에서 파라미터 수집 → 보고서 자동 생성 |
| **자유대화** | On-premise LLM(OpenAI 호환 엔드포인트)과 자유롭게 대화 |
| **RAG 질의** | ChromaDB 기반 보고서 작성 가이드 & 이력 검색 + LLM 답변 |
| **DueDate 대시보드** | `scheduler/due_dates.json`을 읽어 D-7/D-3/D-1 알람 표시 |
| **파일 관리** | 보고서 원천 파일 업로드/목록/삭제 |

---

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

LLM 스트리밍 기능을 사용하려면 아래도 설치하세요 (선택):

```bash
pip install langchain-openai langchain-core
```

RAG(ChromaDB) 기능을 사용하려면 (선택):

```bash
pip install chromadb
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 필요한 값을 채워 넣으세요:

```dotenv
# LLM 엔드포인트 (OpenAI 호환)
LLM_BASE_URL=http://localhost:8000/v1
LLM_API_KEY=dummy
LLM_MODEL=qwen2.5
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_STREAMING=true

# ChromaDB
CHROMA_MODE=local
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=report_guidelines

# DueDate
DUEDATE_REFRESH_SECONDS=60
OUTLOOK_ENABLED=false

# 앱 서버
APP_HOST=0.0.0.0
APP_PORT=8080
APP_TITLE=대외기관 보고서 자동화 Agent
APP_RELOAD=false

# 로그 레벨
LOG_LEVEL=INFO
```

### 3. 앱 실행

```bash
python -m app.main
# 또는
python app/main.py
```

브라우저에서 `http://localhost:8080` 으로 접속하세요.

---

## 디렉토리 구조

```
Reporting-Agent/
├── app/
│   ├── main.py              # NiceGUI 엔트리포인트
│   ├── config.py            # 설정 (env 변수 로드)
│   ├── pages/
│   │   └── home.py          # 메인 페이지 레이아웃
│   ├── components/
│   │   ├── sidebar.py       # 보고서 버튼 / 모드 전환 / 파일 업로드
│   │   ├── chat_window.py   # 채팅 UI + 모드별 처리 로직
│   │   ├── dashboard.py     # DueDate 알람 카드 + 주기 업데이트
│   │   └── file_manager.py  # 업로드 파일 목록/삭제
│   ├── models/
│   │   ├── chat_models.py   # ChatMode / MessageRole / ChatMessage / ReportExecState
│   │   ├── report_models.py # ReportMeta + REPORT_CATALOG
│   │   └── duedate_models.py# DueDateEntry / AlertLevel
│   ├── services/
│   │   ├── llm_client.py    # ChatOpenAI 싱글턴
│   │   ├── chat_service.py  # 자유대화 토큰 스트리밍
│   │   ├── rag_service.py   # ChromaDB 질의 + LLM 답변
│   │   ├── report_runner.py # 보고서 실행 오케스트레이터 (mock)
│   │   └── duedate_service.py# due_dates.json 로드/저장 + 알람 계산
│   └── utils/
│       ├── paths.py         # BASE_DIR 및 data/vectordb/scheduler 경로
│       └── logging.py       # 로거 설정
│
├── data/                    # 보고서 원천 파일 (사용자 업로드)
├── vectordb/chroma_data/    # ChromaDB 영구 저장소
├── scheduler/
│   └── due_dates.json       # DueDate 스케줄 (샘플 포함)
├── requirements.txt
└── README.md
```

---

## 채팅 모드 설명

### 💬 자유대화 (Free Chat)
기본 모드. On-premise LLM과 자유롭게 대화합니다.
LLM이 미연결 상태이면 fallback 메시지를 반환합니다.

### 📚 RAG 질의 (RAG Query)
ChromaDB에서 관련 문서를 검색한 후 LLM이 컨텍스트를 활용해 답변합니다.
VectorDB가 비어 있으면 일반 LLM 답변으로 대체됩니다.

### 📊 보고서 실행 (Report Exec)
사이드바의 보고서 버튼을 클릭하면 활성화됩니다.
채팅창에서 필요한 파라미터를 순차적으로 수집한 후 보고서를 실행합니다.

---

## 보고서 카탈로그 커스터마이징

`app/models/report_models.py`의 `REPORT_CATALOG` 딕셔너리에 보고서를 추가하거나 수정하세요.

```python
"my_report": ReportMeta(
    report_id="my_report",
    label="내 보고서",
    description="설명",
    required_params=[
        ParamSpec("base_date", "기준일자를 입력하세요 (YYYY-MM-DD)", "2026-01-01"),
    ],
),
```

실제 보고서 생성 로직은 `app/services/report_runner.py`의 `ReportRunner.run()` 메서드에 연결하세요.

---

## DueDate 관리

`scheduler/due_dates.json`을 직접 편집하거나 `duedate_service` API를 통해 항목을 추가할 수 있습니다.

Outlook 자동 스캔 기능은 현재 stub 상태입니다.
`OUTLOOK_ENABLED=true`로 설정하고 `app/services/duedate_service.py`의
`scan_outlook_for_due_dates()` 함수를 구현하면 활성화됩니다.

---

## 라이선스

MIT
