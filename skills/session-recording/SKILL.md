---
name: session-recording
description: 사용자가 "녹음시작" / "녹음 시작" / "강의 녹음" / "회의 녹음" / "전사 시작" 이라고 하거나, 실시간 강의·회의·교육 세션의 녹음과 요약을 요청할 때 사용한다. 실시간 전사와 함께 오디오 원본(m4a)도 저장한다. 실행을 멈추는 "녹음종료" / "녹음 끝" 도 이 스킬이 처리한다.
---

# 세션 실시간 녹음·요약 (강의·회의·교육)

whisper-stream으로 마이크 입력을 실시간 전사하고, ffmpeg로 오디오 원본(`session.m4a`)을 병행 저장하며, 10분 간격 루프로 누적 요약과 질문 후보를 갱신한다. 회차 산출물은 전부 작업 디렉터리 아래 `session-<YYYY-MM-DD>/` 안에 모은다 (기존 자료가 `lecture-<날짜>/` 관례를 쓰는 레포면 그 관례를 따른다).

## 전제 조건

- `whisper-stream` 바이너리(whisper.cpp의 stream 예제)와 한국어 지원 모델이 설치돼 있어야 한다. 시작 전에 한 번 확인하고, 없으면 사용자에게 설치 여부를 먼저 묻는다 — 임의로 대용량 모델을 다운로드하지 않는다.
  - 바이너리: `command -v whisper-stream` (macOS는 `brew install whisper-cpp` 계열로 설치 가능)
  - 모델: `~/models/whisper/ggml-large-v3-turbo.bin` (기본 가정 경로 — 다르면 사용자에게 확인)
- 오디오 원본 저장에는 `ffmpeg` 가 필요하다 (`command -v ffmpeg`, macOS 는 `brew install ffmpeg`).
  없으면 사용자에게 설치 여부를 묻고, 설치를 원치 않으면 **전사만으로 진행한다** — 오디오
  저장이 없으면 부정확한 구간을 재청취·재전사할 수 없다는 점을 한 줄 알린다.
- **용어집(glossary)** — 고유명사 오인식을 줄이는 2층 사전 구조를 쓴다:
  - 스킬 내장 공용 사전: `resources/glossary.d/00-common-it.txt` (도메인 무관 IT 용어.
    **프로젝트·회사 고유명사를 여기에 커밋하지 않는다** — 공개 레포다)
  - 로컬 사전: `~/.config/session-recording/glossary.d/*.txt` (개인 전역) 와
    작업 디렉터리의 `glossary.txt` (프로젝트별). 둘 다 없으면 "용어집 없이 시작할까요?"
    를 한 번 묻는다.
  - 형식은 한 줄 한 항목 `정식표기 | 오인식1, 오인식2 | 비고` ('#' 줄과 빈 줄 무시).
- 이미 설치돼 있으면 재설치·재다운로드하지 않는다.

## 트리거

| 사용자 발화 | 동작 |
|---|---|
| `녹음시작`, `녹음 시작`, `강의 녹음 시작`, `회의 녹음 시작`, `전사 시작` | 아래 시작 절차 실행 |
| `녹음종료`, `녹음 끝`, `강의 끝`, `회의 끝` | 아래 종료 절차 실행 |
| `지금까지 요약`, `중간 요약` | 루프 회차 1회를 수동 실행 |

## 시작 절차

1. **세션(강의·회의) 제목·주제를 한 줄 묻는다.** 요약 헤더와 서브에이전트 프롬프트의 도메인 맥락으로 쓴다. 이미 대화에서 알 수 있으면 묻지 않는다.

2. 회차 디렉터리 생성 + 입력 볼륨 설정 + whisper-stream 백그라운드 기동 (프로젝트 루트 기준):

   ```bash
   mkdir -p session-$(date +%F)
   osascript -e 'set volume input volume 70'   # macOS
   # 용어집 병합 → 정식표기만 뽑아 프롬프트로 (내장 공용 + 로컬 전역 + 프로젝트)
   GLOSSARY=$(cat <스킬경로>/resources/glossary.d/*.txt \
                  ~/.config/session-recording/glossary.d/*.txt \
                  ./glossary.txt 2>/dev/null \
              | grep -v '^#' | grep -v '^$' | cut -d'|' -f1 | tr '\n' ',' | tr -s ' ')
   cd session-$(date +%F) && whisper-stream \
     -m ~/models/whisper/ggml-large-v3-turbo.bin \
     -l ko -t 8 --step 3000 --length 10000 \
     --prompt "다음 용어가 등장하는 회의: $GLOSSARY" \
     -f transcript.txt
   ```

   - `--prompt` 는 강제가 아니라 편향이다 — 한도 약 224토큰이므로 용어가 아주 많으면
     이번 세션과 관련 높은 것 위주로 앞쪽에 배치한다.

   - `Bash run_in_background=true`로 띄운다. **`disown` 금지** — harness가 프로세스를 추적하지 못한다.
   - 온라인 세션(Zoom/Teams)이면 마이크 대신 BlackHole 등 시스템 오디오 캡처를 쓰는 게 음질이 낫다. 사용자가 온라인이라고 하면 이 점을 알린다.

3. **오디오 원본 병행 녹음** — ffmpeg 가 있으면 같은 입력을 m4a 로 저장한다 (whisper 와 별개 프로세스, macOS CoreAudio 는 같은 입력 장치의 동시 캡처를 허용한다):

   ```bash
   cd session-$(date +%F) && ffmpeg -f avfoundation -i ":0" -ac 1 -c:a aac -b:a 64k      -movflags +frag_keyframe+empty_moov session.m4a
   ```

   - 역시 `run_in_background=true`, `disown` 금지.
   - `:0` 은 기본 오디오 입력 인덱스다. 장치가 여럿(BlackHole 등)이면
     `ffmpeg -f avfoundation -list_devices true -i ""` 로 인덱스를 확인해 **whisper-stream 과
     같은 입력**을 잡는다.
   - `frag_keyframe+empty_moov` 는 프로세스가 비정상 종료해도 그 시점까지의 오디오가
     재생 가능하게 남도록 하는 안전장치다 (일반 m4a 는 정상 종료 전에 죽으면 통째로 깨진다).
   - AAC 64k 모노 기준 2시간에 약 55MB.

4. **30초쯤 뒤 `transcript.txt`에 실제 텍스트가 쌓이는지, `session.m4a` 크기가 커지는지 한 번 확인하고 보고한다.** transcript 가 비어 있으면 마이크 권한·입력 장치를 먼저 점검한다. 확인 없이 "시작했습니다"만 보고하지 않는다.

5. 요약 루프를 건다 — `loop` 스킬로 10분 간격:

   ```
   /loop 10m 세션 전사 증분 요약 (session-<날짜>)
   ```

6. 읽은 바이트 오프셋을 대화 안에서 계속 들고 간다. 초기값 1.

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
   - **누적 세션 요약** — 이번 구간에서 새로 나온 내용을 기존 요약에 병합. 매 회차 처음부터 다시 쓰지 않는다.
   - **질문 후보** — 강사·발표자에게 물어볼 것. 세션이 진행되며 답이 나온 항목은 목록에서 빼고 새 후보로 교체한다.

4. **쉬는 시간·점심**에는 잡음만 쌓인다. 파일 크기가 늘어도 알맹이가 없으면 "휴식 중, 스트리머 정상" 한 줄로 끝낸다. 억지로 요약을 만들지 않는다.

5. 인식 근거가 없는 내용은 **지어내지 않는다.** 특히 사람 이름·고유명사는 음성으로 확정 불가 — `[불명확]`으로 남긴다.

## 종료 절차

1. whisper-stream 프로세스를 종료한다 (`TaskStop` 또는 `pkill -f whisper-stream`).
   ffmpeg 는 **반드시 SIGINT 로** 종료한다 (`pkill -INT -f 'ffmpeg.*session.m4a'`) — 정상
   마무리 쓰기가 일어나야 하며, `kill -9` 는 마지막 조각을 잃는다. 종료 후
   `ffprobe -v error -show_entries format=duration session.m4a` 로 길이가 세션 시간과
   비슷한지 확인한다.
2. **루프를 반드시 해제한다.** 끝난 뒤에도 계속 돌면 빈 요약이 쌓인다.
3. 최종 산출물을 만든다:
   - `session.m4a` — 오디오 원본. **절대 덮어쓰지 않는다.** 전사가 의심스러운 구간의
     재청취·재전사용 근거다. whisper-cli 는 m4a 를 직접 못 읽으므로(miniaudio 디코더
     한계, 2026-08-02 실측) 재전사는 반드시 변환을 거친다:
     `ffmpeg -i session.m4a -ar 16000 -ac 1 tmp16k.wav && whisper-cli -m <모델> -l ko -f tmp16k.wav`
   - `transcript.txt` — 원본. **절대 덮어쓰지 않는다.**
   - `transcript_<세션>_cleaned.txt` — 정리본. 환각 grep 제거 → 1,000줄 내외로 분할 → sonnet 서브에이전트 3~4개 병렬. 프롬프트에 **세션 맥락 + 용어집 병합본 전체**(오인식 매핑 포함)를 반드시 넣는다 — 출처는 위 전제 조건의 glossary 파일들이다. 없으면 고유명사가 전부 엉뚱하게 복원된다.
   - 세션 중 새로 확정된 용어(사용자가 교정해 준 고유명사)는 **로컬 사전에 추가**한다 — 다음 세션부터 자동 반영된다. 회사·프로젝트 고유명사를 스킬 레포에 커밋하지 않는다.
   - `summary_<세션명>_<날짜>.md` — 보고용 요약본(교육요약·회의록 등 성격에 맞게). 표준/격식 톤.
4. 레포에 회차 기록 표(README 등)가 있으면 한 행 추가한다.
5. 사용자가 매뉴얼 HTML을 원하면 `session-<날짜>/html/`에 만든다 — 모바일 우선 + 데스크톱 동시 확인, `<meta charset="utf-8">` 필수(없으면 한글 전부 깨짐). 표·코드블록은 각자 `overflow-x: auto` 컨테이너에 넣는다.

## 자주 하는 실수

| 실수 | 결과 |
|---|---|
| 매 회차 `transcript.txt` 전체 읽기 | 컨텍스트 폭발. 오프셋 이후만 읽는다. |
| `disown`으로 백그라운드 실행 | harness가 완료·실패 알림을 못 받는다. |
| 환각 필터 없이 요약 | "양념장"이 세션 내용으로 들어간다. |
| 정리본을 `transcript.txt`에 덮어쓰기 | 원본 소실. 복구 불가. |
| 서브에이전트에 용어집 없이 교정 지시 | 고유명사가 전부 창작된다. |
| 프로젝트 고유명사를 내장 사전에 커밋 | 공개 레포에 회사 정보 노출. 로컬 사전에 둔다. |
| --prompt 없이 전사 후 손교정 반복 | 같은 오인식이 세션마다 재발한다. |
| 세션 끝나고 루프 방치 | 빈 요약이 계속 쌓인다. |
| ffmpeg 를 `kill -9` 로 종료 | 마지막 조각 소실. SIGINT 로 종료한다. |
| whisper 와 ffmpeg 가 다른 입력 장치를 잡음 | 전사와 오디오 내용이 어긋난다. 시작 확인 때 둘 다 점검. |
