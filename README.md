# YouTube 다운로더

YouTube 영상을 다운로드하고 PDF로 스크린샷을 생성하는 간단한 프로그램입니다.

## 🚀 빠른 시작

### 1단계: 필요한 프로그램 설치
터미널을 열고 아래 명령어를 **순서대로** 복사해서 붙여넣으세요:

```bash
# 필수 패키지 설치
pip3 install Pillow yt-dlp

# 스크린샷 생성용 (선택사항)
brew install ffmpeg

# PATH 설정 (중요!)
echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2단계: 프로그램 실행
```bash
python3 downloader.py
```

### 3단계: 사용
1. YouTube 링크 붙여넣기
2. 스크린샷 간격 설정 (예: 30초)
3. 원하는 화질 선택
4. 완료! 데스크탑의 `YouTube_Downloads` 폴더에서 확인

## ❗ 문제 해결

### "command not found: python" 오류
```bash
python3 downloader.py
```
(`python` 대신 `python3` 사용)

### "No module named 'PIL'" 오류
```bash
pip3 install Pillow yt-dlp
```

### "No such file or directory: 'yt-dlp'" 오류
```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
python3 downloader.py
```

## 📁 다운로드 위치
모든 파일은 `데스크탑/YouTube_Downloads/영상제목/` 폴더에 저장됩니다.

## ⚠️ 참고사항
개인 용도로만 사용하세요. 저작권을 존중해주세요.