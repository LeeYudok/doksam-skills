---
name: lecture-recording
description: Use when the user says 녹음시작 / 녹음 시작 / 강의 녹음 / 전사 시작, or otherwise asks to record and summarize a live lecture, training session, or meeting. Also covers 녹음종료 / 녹음 끝 to stop the run.
---

# 강의 실시간 녹음·요약

whisper-stream으로 마이크 입력을 실시간 전사하고, 10분 간격 루프로 누적 요약과 질문 후보를 갱신한다. 회차 산출물은 전부 작업 디렉터리 아래 `lecture-<YYYY-MM-DD>/` 안에 모은다.

## 전제 조건

- `whisper-stream` 바이너리(whisper.cpp의 stream 예제)와 한국어 지원 모델이 설치돼 있어야 한다. 시작 전에 한 번 확인하고, 없으면 사용자에게 설치 여부를 먼저 묻는다 — 임의로 대용량 모델을 다운로드하지 않는다.
  - 바이너리: `command -v whisper-stream` (macOS는 `brew install whisper-cpp` 계열로 설치 가능)
  - 모델: `~/models/whisper/ggml-large-v3-turbo.bin` (기본 가정 경로 — 다르면 사용자에게 확인)
- 이미 설치돼 있으면 재설치·재다운로드하지 않는다.

## 트리거

| 사용자 발화 | 동작 |
|---|---|
| `녹음시작`, `녹음 시작`, `강의 녹음 시작`, `전사 시작` | 아래 시작 절차 실행 |
| `녹음종료`, `녹음 끝`, `강의 끝` | 아래 종료 절차 실행 |
| `지금까지 요약`, `중간 요약` | 루프 회차 1회를 수동 실행 |

## 시작 절차

1. **강의 제목·주제를 한 줄 묻는다.** 요약 헤더와 서브에이전트 프롬프트의 도메인 맥락으로 쓴다. 이미 대화에서 알 수 있으면 묻지 않는다.

2. 회차 디렉터리 생성 + 입력 볼륨 설정 + whisper-stream 백그라운드 기동 (프로젝트 루트 기준):

   ```bash
   mkdir -p lecture-$(date +%F)
   osascript -e 'set volume input volume 70'   # macOS
   cd lecture-$(date +%F) && whisper-stream \
     -m ~/models/whisper/ggml-large-v3-turbo.bin \
     -l ko -t 8 --step 3000 --length 10000 \
     -f transcript.txt
   ```

   - `Bash run_in_background=true`로 띄운다. **`disown` 금지** — harness가 프로세스를 추적하지 못한다.
   - 온라인 강의(Zoom/Teams)면 마이크 대신 BlackHole 등 시스템 오디오 캡처를 쓰는 게 음질이 낫다. 사용자가 온라인이라고 하면 이 점을 알린다.

3. **30초쯤 뒤 `transcript.txt`에 실제 텍스트가 쌓이는지 한 번 확인하고 보고한다.** 파일이 비어 있으면 마이크 권한·입력 장치를 먼저 점검한다. 확인 없이 "시작했습니다"만 보고하지 않는다.

4. 요약 루프를 건다 — `loop` 스킬로 10분 간격:

   ```
   /loop 10m 강의 전사 증분 요약 (lecture-<날짜>)
   ```

5. 읽은 바이트 오프셋을 대화 안에서 계속 들고 간다. 초기값 1.

## 매 회차 절차

1. **마지막 오프셋 이후만 읽는다.** 파일 전체 재읽기 금지.

   ```bash
   tail -c +<마지막오프셋> transcript.txt
   wc -c transcript.txt   # 다음 회차 오프셋 = 이 값 + 1
   ```

2. 환각 라인을 걸러낸다. whisper는 무음 구간에서 요리 유튜브 자막풍 문장을 지어낸다:

   ```bash
   tail -c +<오프셋> transcript.txt | grep -v -E "^\s*-?\s*(감사합니다|다음 영상에서 만나요|시청해주셔서 감사합니다|-끝-|- 네\.|고춧가루|양념장.*)\s*!?\.?\s*$"
   ```

3. 보고는 **두 가지**를 갱신한다:
   - **누적 강의 요약** — 이번 구간에서 새로 나온 내용을 기존 요약에 병합. 매 회차 처음부터 다시 쓰지 않는다.
   - **강사 질문 후보** — 강의가 진행되며 답이 나온 항목은 목록에서 빼고 새 후보로 교체한다.

4. **쉬는 시간·점심**에는 잡음만 쌓인다. 파일 크기가 늘어도 알맹이가 없으면 "휴식 중, 스트리머 정상" 한 줄로 끝낸다. 억지로 요약을 만들지 않는다.

5. 인식 근거가 없는 내용은 **지어내지 않는다.** 특히 사람 이름·고유명사는 음성으로 확정 불가 — `[불명확]`으로 남긴다.

## 종료 절차

1. whisper-stream 프로세스를 종료한다 (`TaskStop` 또는 `pkill -f whisper-stream`).
2. **루프를 반드시 해제한다.** 끝난 뒤에도 계속 돌면 빈 요약이 쌓인다.
3. 최종 산출물을 만든다:
   - `transcript.txt` — 원본. **절대 덮어쓰지 않는다.**
   - `transcript_<세션>_cleaned.txt` — 정리본. 환각 grep 제거 → 1,000줄 내외로 분할 → sonnet 서브에이전트 3~4개 병렬. 프롬프트에 **강의 맥락 + 자주 깨지는 용어 매핑**을 반드시 넣는다. 없으면 고유명사가 전부 엉뚱하게 복원된다.
   - `summary_교육요약_<날짜>.md` — 보고용 요약본. 표준/격식 톤.
4. 레포에 회차 기록 표(README 등)가 있으면 한 행 추가한다.
5. 사용자가 매뉴얼 HTML을 원하면 `lecture-<날짜>/html/`에 만든다 — 모바일 우선 + 데스크톱 동시 확인, `<meta charset="utf-8">` 필수(없으면 한글 전부 깨짐). 표·코드블록은 각자 `overflow-x: auto` 컨테이너에 넣는다.

## 자주 하는 실수

| 실수 | 결과 |
|---|---|
| 매 회차 `transcript.txt` 전체 읽기 | 컨텍스트 폭발. 오프셋 이후만 읽는다. |
| `disown`으로 백그라운드 실행 | harness가 완료·실패 알림을 못 받는다. |
| 환각 필터 없이 요약 | "양념장"이 강의 내용으로 들어간다. |
| 정리본을 `transcript.txt`에 덮어쓰기 | 원본 소실. 복구 불가. |
| 서브에이전트에 용어집 없이 교정 지시 | 고유명사가 전부 창작된다. |
| 강의 끝나고 루프 방치 | 빈 요약이 계속 쌓인다. |
