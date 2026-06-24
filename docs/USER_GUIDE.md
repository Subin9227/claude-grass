# Claude Profile Stats 사용 가이드

## 이 문서는 누구를 위한 건가요?

이 문서는:

- Claude를 자주 쓰는 사람
- GitHub 프로필 README에 나만의 사용량 카드를 넣고 싶은 사람
- 개발자가 아니어도 순서대로 따라 하고 싶은 사람

을 위한 안내서입니다.

어려운 말은 최대한 줄이고, 실제로 해야 하는 순서대로 설명합니다.

## 이 도구로 무엇을 할 수 있나요?

이 도구는 내 컴퓨터에 저장된 Claude 사용 기록을 읽어서 아래 파일을 만들어 줍니다.

- `Claude Grass`: GitHub 잔디처럼 보이는 사용 기록 카드
- `Money Copy Card`: 이번 달 Claude를 얼마나 많이 썼는지 보여주는 카드
- `Claude Badges`: 사용 패턴을 뱃지처럼 보여주는 카드

이 카드들은 SVG 이미지 파일로 만들어지고, GitHub 프로필 README에 넣을 수 있습니다.

## 먼저 알아두면 좋은 점

이 도구는 GitHub에서 Claude 사용량을 가져오는 게 아닙니다.

대신 내 컴퓨터 안의 Claude 로컬 기록을 읽습니다.

즉:

- 내 컴퓨터에 Claude 사용 기록이 있어야 합니다
- 이 도구는 내 컴퓨터에서 실행해야 합니다
- 실행한 뒤 만들어진 SVG 파일을 GitHub 프로필 저장소에 올려야 합니다

## 준비물

시작하기 전에 아래가 필요합니다.

### 1. Python 설치

이 도구는 Python으로 실행됩니다.

확인 방법:

`명령 프롬프트` 또는 `PowerShell`에서 아래를 입력하세요.

```bash
python --version
```

버전이 나오면 준비 완료입니다.

예:

```bash
Python 3.10.2
```

### 2. Git 설치

GitHub 저장소를 내려받고 업로드할 때 필요합니다.

확인 방법:

```bash
git --version
```

버전이 나오면 준비 완료입니다.

### 3. GitHub 계정

프로필 README에 카드를 넣으려면 GitHub 계정이 있어야 합니다.

### 4. Claude를 사용한 적이 있어야 함

이 도구는 Claude의 로컬 세션 기록을 읽습니다.

Windows 기준으로 보통:

`C:\Users\내이름\.claude`

아래에 기록이 쌓여 있어야 합니다.

## 용어를 아주 쉽게 설명하면

### 프로필 저장소

GitHub에는 내 프로필 메인 화면을 꾸미는 특별한 저장소가 있습니다.

예를 들어 GitHub 아이디가 `Subin9227`라면, 프로필 저장소 이름도:

`Subin9227`

이어야 합니다.

즉:

- 계정명: `Subin9227`
- 저장소명: `Subin9227`

이 저장소의 `README.md`가 GitHub 프로필 메인에 보입니다.

### 로컬 저장소

내 컴퓨터에 내려받아 놓은 GitHub 폴더입니다.

예:

`C:\Users\82105\Desktop\Subin9227-profile`

## 전체 사용 흐름 한눈에 보기

순서는 딱 이렇습니다.

1. 이 프로젝트를 내 컴퓨터에 내려받기
2. 내 GitHub 프로필 저장소를 내 컴퓨터에 내려받기
3. 설정 파일 수정하기
4. Claude 카드 만들기
5. 프로필 저장소에 카드 복사하기
6. GitHub에 업로드하기

## 1단계: 이 프로젝트 내려받기

원하는 폴더에서 이 프로젝트를 내려받습니다.

예:

```bash
cd C:\Users\82105\Desktop
git clone <이 프로젝트 주소>
```

이미 폴더가 있다면 이 단계는 건너뛰어도 됩니다.

예를 들어 이미 아래 폴더가 있다면:

`C:\Users\82105\Desktop\claude-dashboard`

그 폴더를 그대로 사용하면 됩니다.

## 2단계: 내 GitHub 프로필 저장소 내려받기

### 2-1. 바탕화면으로 이동

`명령 프롬프트` 기준:

```bash
cd C:\Users\82105\Desktop
```

### 2-2. 프로필 저장소 클론

GitHub 아이디가 `Subin9227`라면 예시는 아래와 같습니다.

```bash
git clone https://github.com/Subin9227/Subin9227.git Subin9227-profile
```

이 명령은:

- GitHub의 프로필 저장소를
- 내 컴퓨터 바탕화면에
- `Subin9227-profile`이라는 폴더 이름으로

받아옵니다.

### 2-3. 제대로 받아졌는지 확인

```bash
cd C:\Users\82105\Desktop\Subin9227-profile
git remote -v
```

정상이라면 GitHub 주소가 나옵니다.

## 3단계: 설정 파일 수정하기

이제 Claude Profile Stats 프로젝트 폴더로 돌아갑니다.

```bash
cd C:\Users\82105\Desktop\claude-dashboard
```

프로젝트 안에 있는 `config.toml` 파일을 엽니다.

예시:

```toml
[paths]
claude_base = "C:/Users/82105/.claude"
profile_repo = "C:/Users/82105/Desktop/Subin9227-profile"
database = "./data/profile.db"
output_dir = "./output"

[profile]
github_username = "Subin9227"
plan_monthly_price_usd = 20.0

[grass]
days = 180
levels = [0, 250000, 1000000, 3000000]
```

### 꼭 바꿔야 하는 항목

#### `profile_repo`

이 값은 내 GitHub 프로필 저장소의 로컬 폴더 경로여야 합니다.

예:

```toml
profile_repo = "C:/Users/82105/Desktop/Subin9227-profile"
```

#### `github_username`

내 GitHub 아이디로 넣습니다.

예:

```toml
github_username = "Subin9227"
```

#### `plan_monthly_price_usd`

내가 기준으로 삼고 싶은 월 요금입니다.

예:

- Claude Pro를 기준으로 보고 싶으면 `20.0`
- 다른 기준을 쓰고 싶으면 바꿔도 됩니다

## 4단계: 카드 생성하기

이제 Claude 기록을 읽어서 카드 파일을 만듭니다.

```bash
python -m claude_profile_stats.app all --config config.toml
```

정상이라면 비슷한 메시지가 나옵니다.

```bash
Synced ... sessions into ...
Rendered assets into ...
```

이 단계가 끝나면 `output` 폴더 안에 파일이 생깁니다.

### 생성되는 파일

- `output/claude-grass.svg`
- `output/money-copy-card.svg`
- `output/claude-badges.svg`
- `output/profile-summary.json`

## 5단계: 프로필 저장소에 복사하기

이제 만들어진 결과물을 내 GitHub 프로필 저장소에 복사합니다.

```bash
python -m claude_profile_stats.app publish --config config.toml
```

정상이라면 비슷한 메시지가 나옵니다.

```bash
Published 4 files into ...\assets and wrote ...\README.md
```

이 단계가 끝나면 내 프로필 저장소 폴더 안에:

- `assets/claude-grass.svg`
- `assets/money-copy-card.svg`
- `assets/claude-badges.svg`
- `assets/profile-summary.json`

이 생깁니다.

또한 `README.md`에 `Claude Karma` 섹션이 추가되거나 갱신됩니다.

## 6단계: GitHub에 업로드하기

이제 실제 GitHub로 올립니다.

### 6-1. 프로필 저장소로 이동

```bash
cd C:\Users\82105\Desktop\Subin9227-profile
```

### 6-2. 변경사항 확인

```bash
git status
```

보통 아래처럼 보입니다.

- `modified: README.md`
- `untracked: assets/`

정상입니다.

### 6-3. 업로드할 파일 준비

```bash
git add README.md assets
```

### 6-4. 커밋

```bash
git commit -m "Add Claude profile stats assets"
```

### 6-5. 푸시

```bash
git push
```

이제 GitHub 프로필 페이지를 새로고침하면 카드가 보여야 합니다.

## 이후에는 어떻게 업데이트하나요?

처음 한 번만 설정하면, 다음부터는 보통 아래 두 줄이면 됩니다.

```bash
cd C:\Users\82105\Desktop\claude-dashboard
python -m claude_profile_stats.app all --config config.toml
python -m claude_profile_stats.app publish --config config.toml
```

그 다음 프로필 저장소 폴더에서:

```bash
cd C:\Users\82105\Desktop\Subin9227-profile
git add README.md assets
git commit -m "Update Claude profile stats"
git push
```

## 자주 생기는 문제와 해결법

### 문제 1. `python --version`이 안 돼요

Python이 설치되지 않았거나 PATH 설정이 안 된 것입니다.

해결:

- Python 설치
- 설치할 때 PATH 추가 옵션 체크

### 문제 2. `git`이 안 돼요

Git이 설치되지 않았거나 PATH 설정이 안 된 것입니다.

해결:

- Git for Windows 설치

### 문제 3. 이미지가 GitHub에서 깨져 보여요

가장 흔한 원인:

- `README.md`만 바뀌고 `assets/*.svg`가 GitHub에 아직 안 올라감
- 상대경로는 맞는데 실제 파일이 원격 저장소에 없음

확인:

- GitHub 저장소 안에 `assets` 폴더가 있는지
- 그 안에 SVG 파일이 있는지

해결:

```bash
git add README.md assets
git commit -m "Add assets"
git push
```

### 문제 4. 기존 README 글이 사라졌어요

이전 버전 퍼블리시 로직에서 `README.md`를 통째로 덮어쓸 수 있었습니다.

현재 버전은:

- 기존 README를 유지하고
- `Claude Karma` 섹션만 추가/갱신하도록 수정되어 있습니다

만약 아직 커밋하지 않았다면 복구:

```bash
git restore README.md
```

그리고 다시 publish 하세요.

### 문제 5. `fatal: destination path ... already exists`

이미 같은 이름의 폴더가 있다는 뜻입니다.

해결:

- 기존 폴더를 확인해서 진짜 Git 저장소인지 보기
- 아니면 다른 이름으로 클론

예:

```bash
git clone https://github.com/Subin9227/Subin9227.git Subin9227-profile
```

### 문제 6. `fatal: not a git repository`

그 폴더는 Git 저장소가 아닙니다.

해결:

- 올바른 폴더로 이동했는지 확인
- 프로필 저장소를 실제로 클론했는지 확인

## 추천 폴더 구조

Windows 바탕화면 기준 예시:

```text
C:\Users\82105\Desktop\
  claude-dashboard\
  Subin9227-profile\
```

이렇게 두 폴더를 분리해 두는 것이 가장 편합니다.

## 추천 사용 순서 요약

정말 간단히 요약하면:

### 처음 한 번만

1. Claude Profile Stats 프로젝트 준비
2. GitHub 프로필 저장소 클론
3. `config.toml` 수정

### 그 다음부터 반복

1. `all` 실행
2. `publish` 실행
3. 프로필 저장소 `git add`
4. `git commit`
5. `git push`

## 명령어만 빠르게 보고 싶은 사람용

### 카드 생성

```bash
cd C:\Users\82105\Desktop\claude-dashboard
python -m claude_profile_stats.app all --config config.toml
```

### 프로필 저장소에 복사

```bash
python -m claude_profile_stats.app publish --config config.toml
```

### GitHub에 업로드

```bash
cd C:\Users\82105\Desktop\Subin9227-profile
git add README.md assets
git commit -m "Update Claude profile stats"
git push
```

## 마지막 팁

처음에는 무조건:

- `publish` 전에 `all`
- `push` 전에 `git status`

이 두 가지만 습관처럼 확인하면 실수를 많이 줄일 수 있습니다.

