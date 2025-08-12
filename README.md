<div align="right">
  <b>한국어</b> | <a href="README.en.md">English</a>
</div>

# YouTube Short Downloader (Screeenshot+PDF) 

YouTube 동영상을 원하는 화질로 다운로드하고, 일정 간격으로 스크린샷을 추출한 뒤 하나의 PDF로 묶어주는 간단한 CLI 도구입니다.

## ✅ 사용 가이드 
<img width="1011" height="623" alt="Image" src="https://github.com/user-attachments/assets/55252672-8e3a-455f-806b-d168f0e708a4" />
<img width="1011" height="623" alt="Image" src="https://github.com/user-attachments/assets/6fee779b-d312-44f5-bf8b-d9863f56dc74" />

## ✨ 주요 기능
- **동영상 다운로드**: `yt-dlp`를 사용해 오디오 포함 포맷을 선택하여 저장
- **화질/코덱 선택**: 사용 가능한 포맷 목록을 보여주고 사용자가 직접 선택
- **스크린샷 추출**: `ffmpeg`로 N초 간격의 프레임을 이미지로 저장
- **PDF 생성**: 추출된 스크린샷을 `Pillow`로 하나의 PDF 파일로 병합
- **예상 크기 표시**: 스크린샷 간격을 바탕으로 PDF 예상 용량(대략)을 안내
- **안전한 저장 위치**: `데스크탑/YouTube_Downloads/동영상제목/`에 결과물 정리 저장
- **YouTube Shorts 최적화**: 세로(9:16) 영상에 맞춘 권장 간격과 해상도 선택 가이드 제공

## 🧩 동작 개요
1) URL 입력 → 2) 스크린샷 간격(초) 입력 → 3) 사용 가능한 포맷 목록 확인 → 4) 화질 번호 선택 → 5) 다운로드 → 6) 스크린샷 추출 → 7) PDF 생성

PDF 예상 용량은 스크린샷 1장 ≈ 200KB로 가정하여 \( \lfloor duration / interval \rfloor \times 200KB \)로 계산합니다.

## 🎯 YouTube Shorts 최적화
- **권장 간격(Shorts 기준)**: 1–3초
  - 예: 60초 영상, 2초 간격 → 약 30장 → 대략 6MB(200KB × 30)
- **권장 해상도(세로)**: `1080x1920`, `720x1280` 등 세로 비율(9:16)에 맞는 항목 선택
  - 목록에 가로(`1920x1080`)와 세로(`1080x1920`)가 섞여 보일 수 있으니 세로 해상도를 선택하세요
- **URL 형태**: `https://www.youtube.com/shorts/...` 형태의 링크도 그대로 입력하면 동작합니다
- **처리 속도**: 영상 길이가 짧아 다운로드/프레임 추출/병합까지 빠르게 완료됩니다

## 🚀 빠른 시작 (macOS)

### 1) 필수 도구 설치
터미널에서 아래 명령을 순서대로 실행하세요.

```bash
# Python 패키지 설치
python3 -m pip install --upgrade pip
python3 -m pip install Pillow yt-dlp

# 스크린샷(프레임 추출)용 도구
brew install ffmpeg

# (선택) pip 유틸리티 기본 경로를 PATH에 추가
echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# 설치 확인
yt-dlp --version
ffmpeg -version
```

> Apple Silicon(M1/M2) 환경에서 `yt-dlp`가 `/opt/homebrew/bin/yt-dlp`에 설치될 수 있습니다. 본 프로젝트는 실행 시 자동으로 대표 설치 경로를 탐색합니다.

### 2) 실행
```bash
python3 downloader.py
```

### 3) 사용 흐름
1. 유튜브 URL을 입력합니다
2. 스크린샷 간격(초)을 입력합니다 (예: `30`)
3. 표시된 목록에서 원하는 화질 번호를 선택합니다
4. 완료 후 `데스크탑/YouTube_Downloads/영상제목/` 폴더에서 결과를 확인합니다

## 📁 출력물 구조
예: 동영상 제목이 `My Video`인 경우

```
Desktop/
└── YouTube_Downloads/
    └── My Video/
        ├── My Video.mp4          # 선택한 포맷으로 저장된 동영상
        ├── screenshots/          # 스크린샷 이미지 모음
        │   ├── screenshot_0001.png
        │   ├── screenshot_0002.png
        │   └── ...
        └── My Video_screenshots.pdf  # 이미지들을 하나로 합친 PDF
```

## ⚙️ 세부 동작 및 옵션
- **포맷 표시**: 오디오가 포함된 포맷만 목록에 보여줍니다.
- **용량 표시**: 각 포맷의 파일 크기(가능한 경우)와 함께 PDF 예상 용량을 함께 표시합니다.
- **간격(초)**:
  - Shorts(≤60초): `1~3초` 권장
  - 일반 영상: `10~60초` 권장

## 💡 사용 예시 (콘솔)
```
유튜브 URL을 입력하세요: https://www.youtube.com/watch?v=EXAMPLE
몇 초 간격으로 스크린샷을 추출하시겠습니까? 30

사용 가능한 비디오 포맷:
--------------------------------------------------------------------------------
번호 해상도    파일(예상)      PDF(예상)            코덱
--------------------------------------------------------------------------------
1    1920x1080  120.45 MB      8.00 MB              avc1
2    1280x720   80.12 MB       8.00 MB              avc1
...
--------------------------------------------------------------------------------
다운로드할 포맷의 번호를 선택하세요 (취소하려면 'q' 입력): 2

'Desktop/YouTube_Downloads/My Video' 폴더에 다운로드를 시작합니다...
다운로드 완료!
스크린샷 생성을 시작합니다 (30초 간격)...
스크린샷 생성 완료.
'.../My Video_screenshots.pdf' 이름으로 PDF 파일 생성을 시작합니다...
PDF 생성 완료!
```

## 🔍 문제 해결
- **python 명령이 안 될 때**: `python3 downloader.py`로 실행하세요.
- **Pillow 모듈 오류(`No module named 'PIL'`)**: `python3 -m pip install Pillow` 재설치
- **yt-dlp를 찾을 수 없음**:
  - `python3 -m pip install yt-dlp` 후 `yt-dlp --version`으로 확인
  - PATH 문제일 수 있으니 `echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc`
  - Apple Silicon의 경우 `/opt/homebrew/bin/yt-dlp`에 설치될 수 있음
- **ffmpeg를 찾을 수 없음**:
  - `brew install ffmpeg` 후 `ffmpeg -version`으로 확인
  - 여전히 안 되면 터미널을 새로 열거나 `source ~/.zshrc`
- **권한 오류 / 설치 경로 충돌**: 가상환경 사용을 권장합니다.
  - `python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install Pillow yt-dlp`

## 🛡️ 저작권 및 이용 약관
- 본 도구는 **개인적/교육적 용도**를 위해 제공됩니다.
- 각 플랫폼의 **서비스 약관**과 **저작권 법**을 준수하세요. 저작권자가 허용하지 않은 콘텐츠의 다운로드/배포는 불법일 수 있습니다.

## 🧱 기술 스택
- `yt-dlp`: 동영상/오디오 다운로드 및 포맷 정보 조회
- `ffmpeg`: 프레임 추출(스크린샷 생성)
- `Pillow(PIL)`: 이미지 → PDF 병합
- Python 표준 라이브러리: `subprocess`, `json`, `os`, `shutil`

## 🔧 내부 구현(간단 설명)
- `find_ytdlp_path()`: 대표 설치 경로들을 순회하며 `yt-dlp` 위치 탐색
- `get_video_info(url)`: `yt-dlp -j`로 포맷/메타데이터 조회
- `display_formats(...)`: 선택 가능한 포맷 목록 + PDF 예상 크기 출력
- `download_video(...)`: 선택 포맷으로 다운로드 후 결과 경로 반환
- `take_screenshots_and_create_pdf(...)`: `ffmpeg`로 PNG 추출 → `Pillow`로 PDF 병합

## 🗺️ 로드맵(아이디어)
- 자동 화질/용량 기준 선택 옵션 제공(예: 720p 이상 중 가장 작은 파일)
- 스크린샷 해상도/품질 조절 옵션
- GUI 간단 실행기(드래그앤드롭)

## 🙋 자주 묻는 질문(FAQ)
- **Shorts도 지원하나요?** 네. 본 도구는 Shorts 워크플로에 최적화되어 있으며, 세로 해상도 선택과 1–3초 간격 설정을 권장합니다.
- **YouTube 외 사이트도 되나요?** 현재 가이드는 YouTube 기준이며, 내부적으로 `yt-dlp`를 사용하므로 다른 사이트도 일부 동작할 수 있으나 보장하지 않습니다.
- **PDF가 너무 커요**: 간격을 늘리거나, 스크린샷 해상도를 낮추는 옵션이 추후 추가될 예정입니다.

---
문의/개선 제안은 이 저장소의 이슈로 남겨주세요. 감사합니다!