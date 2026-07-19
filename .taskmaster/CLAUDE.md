# Task Master 작업 안내

이 파일은 Task Master CLI와 MCP를 사용하는 저장소 도구를 위한 참고 문서입니다. 실제 작업
상태의 기준은 `.taskmaster/tasks/tasks.json`이며 직접 편집하지 않습니다.

## 기본 명령

```bash
# 현재 태스크와 다음 태스크
task-master list
task-master next
task-master show <id>

# 상태 변경
task-master set-status --id=<id> --status=in-progress
task-master set-status --id=<id> --status=done

# 진행 내용 기록
task-master update-subtask --id=<id> --prompt="구현과 검증 내용"

# 의존성 확인
task-master validate-dependencies
task-master fix-dependencies
```

## PRD에서 태스크 만들기

```bash
task-master parse-prd .taskmaster/docs/prd.txt
task-master analyze-complexity --research
task-master expand --all --research
```

기존 태스크에 새 PRD 내용을 붙일 때만 `--append`를 사용합니다. 파싱 전에 PRD의 범위와
의존성, 완료 기준을 확인하세요.

## 태스크 관리 원칙

1. `task-master next`로 의존성이 해소된 작업을 확인합니다.
2. 구현 전 상태를 `in-progress`로 바꿉니다.
3. 관련 코드와 테스트를 읽고 현재 동작을 확인합니다.
4. 구현 중 중요한 결정과 발견을 하위 태스크에 기록합니다.
5. 테스트와 리뷰 근거가 있을 때만 `done`으로 바꿉니다.

태스크가 어렵다는 이유만으로 완료 처리하거나 잘게 나누지 않습니다. 분해가 필요하면 각 하위
태스크가 독립적으로 검증 가능한 결과를 갖도록 합니다.

## 복잡한 작업 분해

```bash
# 단일 태스크 분해
task-master expand --id=<id> --research --force

# 새 하위 태스크 추가
task-master add-subtask --parent=<id> --title="제목" --description="설명"

# 의존성 추가·삭제
task-master add-dependency --id=<id> --depends-on=<id>
task-master remove-dependency --id=<id> --depends-on=<id>
```

순환 의존성을 만들지 않습니다. 기반 모듈, 데이터 계층, 공개 경계, 통합 검증 순서로 위상 정렬이
가능해야 합니다.

## 모델 설정

```bash
task-master models
task-master models --setup
task-master models --set-main <model>
task-master models --set-research <model>
task-master models --set-fallback <model>
```

`.taskmaster/config.json`은 `task-master models`로 관리하고 직접 편집하지 않습니다. API 키는
`.env` 또는 MCP 호스트 환경 변수에 둡니다.

## MCP와 CLI 대응

Task Master MCP가 연결되어 있으면 목록·조회·상태 변경 도구를 사용할 수 있습니다. MCP가
연결되지 않으면 같은 작업을 CLI로 수행합니다. 도구 이름은 설치 버전에 따라 달라질 수 있으므로
현재 `task-master --help`와 MCP 도구 목록을 기준으로 합니다.

## 파일 관리

- `.taskmaster/tasks/tasks.json`: 태스크 기준 데이터, 직접 편집 금지
- `.taskmaster/tasks/task_*.txt`: 자동 생성 파일
- `.taskmaster/config.json`: 모델 설정, 직접 편집 금지
- `.taskmaster/docs/`: PRD와 설계 문서
- `.taskmaster/reports/`: 복잡도 분석 결과

기준 JSON을 수동으로 고친 경우에는 다음 명령으로 파생 파일을 다시 만들지만, 가능한 한 CLI를
사용합니다.

```bash
task-master generate
```

## Git 연동

태스크 ID가 있으면 브랜치, 커밋, PR 설명에서 관련성을 명확히 남길 수 있습니다. 단, 저장소의
기존 브랜치·커밋 규칙을 우선합니다.

```bash
git switch -c feature/<task-id>-short-description
git commit -m "feat: 구현 내용 (<task-id>)"
```

여러 작업을 병렬로 수행할 때는 작업 트리를 분리하고 같은 파일을 동시에 수정하지 않습니다.

## 문제 해결

```bash
# 모델과 인증 확인
task-master models

# 태스크 파일 재생성
task-master generate

# 의존성 검사와 복구
task-master validate-dependencies
task-master fix-dependencies
```

Task Master가 이미 초기화된 저장소에서 다시 초기화하지 않습니다. 초기화는 기존 설정과 태스크를
대체할 수 있으므로 사용자가 명시적으로 요청한 경우에만 수행합니다.

## AI 호출이 필요한 명령

`parse-prd`, `analyze-complexity`, `expand`, `add-task`, `update`, `update-task`,
`update-subtask`는 모델 호출을 사용할 수 있습니다. 실행 시간이 길거나 비용이 발생할 수 있으며,
실패하면 부분 변경 여부를 확인한 뒤 재시도합니다.

`--research`는 연구 모델이 설정된 경우에만 사용합니다. 현재 문서·코드 확인 없이 연구 결과를
사실로 간주하지 않습니다.
