# 명령어 실행 시스템 구현 계획 (Command Execution System Plan)

이 문서는 Gemini Agent가 OS에 구애받지 않고 안전하게 시스템 명령어를 실행하기 위한 설계 내용을 기술합니다.

## 1. 개요 (Overview)

Agent가 직접 쉘 스크립트를 생성하여 실행하는 방식은 위험할 수 있으며, OS 환경(Windows/Linux/Mac)에 따라 문법이 달라 오류가 발생하기 쉽습니다. 
따라서, Agent는 **JSON 형태의 정형화된 요청**만 보내고, 실제 실행은 **Python 기반의 안전한 래퍼(Wrapper)**가 담당하는 구조를 채택합니다.

## 2. 시스템 아키텍처 (Architecture)

### 2.1 OS 감지 및 대응 (OS Awareness)
파이썬의 `platform` 및 `os` 모듈을 사용하여 런타임에 OS를 감지하고, 적절한 명령어로 변환합니다.

- **Windows**: `dir`, `type`, `move`, 백슬래시(`\`) 경로 처리
- **Linux/Mac**: `ls`, `cat`, `mv`, 슬래시(`/`) 경로 처리

### 2.2 통신 인터페이스 (JSON Interface)
Agent는 다음과 같은 JSON 포맷으로 도구를 호출합니다.

```json
{
  "action": "list_directory",
  "params": {
    "path": "./docs"
  }
}
```

```json
{
  "action": "git_status",
  "params": {}
}
```

### 2.3 안전 장치 (Safety Layer)
Python 래퍼에서 요청을 받아 다음과 같은 검증을 거친 후 `subprocess`로 실행합니다.

1.  **명령어 화이트리스트 (Allowlist)**: 사전에 정의된 안전한 작업(`ls`, `mkdir`, `git` 등)만 허용합니다.
2.  **경로 샌드박싱 (Path Sandboxing)**: 프로젝트 루트 디렉토리를 벗어나는 경로(`../../windows/system32` 등) 접근을 차단합니다.
3.  **사용자 승인 (User Approval)**: 파괴적인 작업(삭제 등)이나 불확실한 명령어는 실행 전 사용자에게 확인을 요청할 수 있습니다 (Global setting 의존).

## 3. 구현 상세 (Implementation Details)

`src/mcp_server/system.py`를 생성하여 MCP(Model Context Protocol) 서버로 동작하게 합니다.

### 지원 예정 명령어 (Actions)

| Action Name | Description | Windows Cmd | Unix Cmd |
| :--- | :--- | :--- | :--- |
| `list_directory` | 폴더 내용 조회 | `dir /B` (또는 `os.listdir`) | `ls -1` (또는 `os.listdir`) |
| `read_file` | 파일 내용 읽기 | `type` (또는 `open()`) | `cat` (또는 `open()`) |
| `make_directory` | 폴더 생성 | `mkdir` (또는 `os.makedirs`) | `mkdir -p` |
| `move_item` | 파일/폴더 이동 | `move` (또는 `shutil.move`) | `mv` |
| `copy_item` | 파일/폴더 복사 | `copy` / `xcopy` | `cp` / `cp -r` |
| `git_cmd` | Git 명령어 실행 | `git` | `git` |

### Python 래퍼 예시 (Pseudocode)

```python
import platform
import subprocess
import os

CURRENT_OS = platform.system() # 'Windows', 'Linux', 'Darwin'

def execute_action(action, params):
    if action == "list_directory":
        path = params.get("path", ".")
        # 안전한 경로인지 검증
        validate_path(path) 
        
        # Python 내장 함수 사용이 가장 안전하고 OS 독립적임
        try:
            return str(os.listdir(path))
        except Exception as e:
            return f"Error: {str(e)}"

    elif action == "git_cmd":
        subcmd = params.get("subcommand") # status, add, commit...
        if subcmd not in ["status", "diff", "log", "add", "commit", "push", "pull"]:
             return "Error: Disallowed git subcommand"
        
        # Git은 OS 공통
        return subprocess.check_output(["git", subcmd] + params.get("args", []), text=True)
```

## 4. Git 통합 전략

Git 명령어는 프로젝트 버전 관리를 위해 필수적입니다. 하지만 `git commit`과 같이 편집기가 실행되거나 인터랙티브한 입력이 필요한 경우 Agent가 멈출 수 있습니다.

- **Non-interactive 모드 강제**: `git` 실행 시 `--no-pager`, `-m` 옵션 등을 적극 활용하여 사용자 입력을 기다리는 상황을 방지합니다.
- **Paging 비활성화**: 출력이 너무 길어 짤리는 것을 방지하기 위해 `GIT_PAGER=cat` 환경변수를 설정합니다.

## 5. 다음 단계 (Next Steps)

1. `src/mcp_server/system.py` 파일 생성 및 MCP 서버 구현.
2. `gemini-cli`에 해당 MCP 서버 등록.
3. `tests/test_commands.py`를 통해 OS별 동작 검증.
