import os
import subprocess
import json
import shutil
import time
import threading
from datetime import datetime
from PIL import Image

def find_yt_dlp():
    """yt-dlp 실행파일의 경로를 찾습니다."""
    # 먼저 PATH에서 찾기
    yt_dlp_path = shutil.which('yt-dlp')
    if yt_dlp_path:
        return yt_dlp_path
    
    # Python 사용자 설치 경로에서 찾기
    import sys
    user_base = subprocess.run([sys.executable, '-m', 'site', '--user-base'], 
                              capture_output=True, text=True).stdout.strip()
    if user_base:
        user_bin_path = os.path.join(user_base, 'bin', 'yt-dlp')
        if os.path.exists(user_bin_path):
            return user_bin_path
    
    # 일반적인 경로들 확인
    common_paths = [
        '/usr/local/bin/yt-dlp',
        '/opt/homebrew/bin/yt-dlp',
        os.path.expanduser('~/Library/Python/3.10/bin/yt-dlp'),
        os.path.expanduser('~/Library/Python/3.11/bin/yt-dlp'),
        os.path.expanduser('~/Library/Python/3.12/bin/yt-dlp'),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def show_progress_indicator(message="처리 중", stop_event=None):
    """프로그레스 인디케이터를 표시합니다."""
    spinner = [
        '▂▃▄▅▆▇',
        '▁▂▃▄▅▆',
        '▁▁▂▃▄▅',
        '▁▁▁▂▃▄',
        '▁▁▁▁▂▃',
        '▁▁▁▁▁▂',
        '▁▁▁▁▁▁',
        '▂▁▁▁▁▁',
        '▃▂▁▁▁▁',
        '▄▃▂▁▁▁',
        '▅▄▃▂▁▁',
        '▆▅▄▃▂▁'
    ]
    idx = 0
    
    while not stop_event.is_set():
        print(f"\r{message}... [{spinner[idx % len(spinner)]}] ", end="", flush=True)
        idx += 1
        time.sleep(0.12)
    
    print(f"\r{message}... [완료!] ✅")

def get_video_info(url):
    """yt-dlp를 사용하여 전체 비디오 정보를 JSON으로 가져옵니다."""
    yt_dlp_path = find_yt_dlp()
    if not yt_dlp_path:
        print("오류: yt-dlp가 설치되어 있지 않습니다. 'pip install yt-dlp'로 설치해주세요.")
        return None
    
    clients = ['android', 'ios', 'tv']
    
    # 프로그레스 인디케이터 시작
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_indicator, args=("정보를 가져오는 중", stop_event))
    progress_thread.start()
    
    for client in clients:
        try:
            command = [yt_dlp_path, '-j', '--extractor-args', f'youtube:player-client={client}', '--retries', '3', '--no-check-certificate', url]
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            stop_event.set()
            progress_thread.join()
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            continue
    
    stop_event.set()
    progress_thread.join()
    print(f"\r오류: 모든 클라이언트로 비디오 정보를 가져올 수 없습니다. URL을 확인하세요.")
    return None

def display_formats(formats, duration, interval_seconds):
    """사용자에게 선택할 수 있는 비디오 포맷을 표시합니다."""
    print("\n사용 가능한 비디오 포맷:")
    
    estimated_pdf_size_str = "N/A"
    if duration and interval_seconds > 0:
        num_screenshots = duration // interval_seconds
        # 스크린샷 한 장당 평균 200KB로 가정하여 계산
        estimated_pdf_size_kb = num_screenshots * 200
        if estimated_pdf_size_kb > 1024:
            estimated_pdf_size_str = f"{estimated_pdf_size_kb / 1024:.2f} MB"
        else:
            estimated_pdf_size_str = f"{estimated_pdf_size_kb:.2f} KB"

    print("-" * 95)
    print("{:<4} {:<12} {:<14} {:<19} {:<24} {:<20}".format("번호", "해상도", "파일(예상)", "PDF(예상)", "코덱", "설명"))
    print("-" * 95)

    display_list = []
    all_formats = []
    
    # 모든 사용 가능한 포맷 수집
    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
            filesize = f.get('filesize') or f.get('filesize_approx')
            if filesize:  # 파일 크기가 있는 것만
                all_formats.append({
                    'format': f,
                    'filesize_mb': filesize / 1024 / 1024,
                    'resolution': f.get('resolution', 'N/A')
                })
    
    # 파일 크기 순으로 정렬 (큰 것부터)
    all_formats.sort(key=lambda x: x['filesize_mb'], reverse=True)
    
    if not all_formats:
        return display_list
    
    # 가장 큰 포맷 (원본 품질)
    best_format = all_formats[0]
    filesize_str = f"{best_format['filesize_mb']:.2f} MB"
    original_option = {
        'id': best_format['format']['format_id'],
        'resolution': best_format['resolution'],
        'filesize': filesize_str,
        'filesize_mb': best_format['filesize_mb'],
        'vcodec': best_format['format'].get('vcodec', 'N/A'),
        'description': '원본 품질'
    }
    display_list.append(original_option)
    
    # 원본이 5MB 이상이면 저용량 옵션 추가
    if best_format['filesize_mb'] > 5:
        # 5MB 미만인 가장 큰 포맷 찾기
        found_low_quality = False
        for fmt in all_formats:
            if fmt['filesize_mb'] < 5:
                filesize_str = f"{fmt['filesize_mb']:.2f} MB"
                low_quality_option = {
                    'id': fmt['format']['format_id'],
                    'resolution': fmt['resolution'],
                    'filesize': filesize_str,
                    'filesize_mb': fmt['filesize_mb'],
                    'vcodec': fmt['format'].get('vcodec', 'N/A'),
                    'description': '저용량 (5MB 미만)'
                }
                display_list.append(low_quality_option)
                found_low_quality = True
                break
        
    for i, item in enumerate(display_list):
        print("{:<5} {:<15} {:<18} {:<22} {:<15} {:<20}".format(
            i + 1, item['resolution'], item['filesize'], estimated_pdf_size_str, 
            item['vcodec'], item['description']
        ))
    
    print("-" * 95)
    
    # 5MB 미만 옵션이 없는 경우 경고 메시지 (표 아래에)
    if best_format['filesize_mb'] > 5:
        found_low_quality = any(fmt['filesize_mb'] < 5 for fmt in all_formats)
        if not found_low_quality:
            print("⚠️  5MB 미만 옵션이 없습니다. 원본 품질만 사용 가능합니다.")
    
    return display_list

def download_video(url, format_id, video_title):
    """선택한 포맷으로 비디오를 다운로드하고, 파일 경로를 반환합니다."""
    yt_dlp_path = find_yt_dlp()
    if not yt_dlp_path:
        print("오류: yt-dlp가 설치되어 있지 않습니다.")
        return None
    
    # 파일명 길이 제한 (macOS 호환성)
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()
    if len(safe_title) > 50:  # 50자로 제한 (한글 고려)
        safe_title = safe_title[:50].rstrip()
    
    # 맥의 다운로드 폴더 사용
    downloads_path = os.path.expanduser('~/Downloads')
    download_folder = os.path.join(downloads_path, safe_title)
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    output_template = os.path.join(download_folder, f'{safe_title}.%(ext)s')
    
    # 작동하는 클라이언트 찾기
    clients = ['android', 'ios', 'tv']
    working_client = None
    
    for client in clients:
        try:
            info_command = [yt_dlp_path, '-j', '-f', format_id, '--extractor-args', f'youtube:player-client={client}', '--no-check-certificate', url]
            result = subprocess.run(info_command, capture_output=True, text=True, check=True, timeout=15)
            video_info = json.loads(result.stdout)
            working_client = client
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            continue
    
    if not working_client:
        print("오류: 다운로드 가능한 클라이언트를 찾을 수 없습니다.")
        return None
        
    ext = video_info.get('ext', 'mp4')
    final_video_path = os.path.join(download_folder, f'{safe_title}.{ext}')

    print(f"\n'{download_folder}' 폴더에 다운로드를 시작합니다...")
    command = [yt_dlp_path, '-f', format_id, '-o', output_template, '--extractor-args', f'youtube:player-client={working_client}', '--retries', '3', '--no-check-certificate', url]
    
    # 다운로드 프로그레스 인디케이터 시작
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_indicator, args=("다운로드 중", stop_event))
    progress_thread.start()
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        stop_event.set()
        progress_thread.join()
        print("\n다운로드 완료!")
        return final_video_path
    except subprocess.CalledProcessError as e:
        stop_event.set()
        progress_thread.join()
        print("\n다운로드 중 오류가 발생했습니다.")
        print(e)
        return None

def take_screenshots_and_create_pdf(video_path, interval_seconds):
    """ffmpeg로 스크린샷을 찍고 PDF로 합칩니다."""
    if not video_path or not os.path.exists(video_path):
        print("오류: 비디오 파일이 없습니다.")
        return

    video_dir = os.path.dirname(video_path)
    video_filename = os.path.splitext(os.path.basename(video_path))[0]
    screenshots_dir = os.path.join(video_dir, 'screenshots')
    pdf_path = os.path.join(video_dir, f'{video_filename}_screenshots.pdf')

    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    print(f"\n스크린샷 생성을 시작합니다 ({interval_seconds}초 간격)...")
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps=1/{interval_seconds}',
        os.path.join(screenshots_dir, 'screenshot_%04d.png')
    ]

    # 스크린샷 생성 프로그레스 인디케이터 시작
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_indicator, args=("스크린샷 생성 중", stop_event))
    progress_thread.start()

    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        stop_event.set()
        progress_thread.join()
        print("스크린샷 생성 완료.")
    except FileNotFoundError:
        stop_event.set()
        progress_thread.join()
        print("\n오류: ffmpeg가 설치되어 있지 않거나 PATH에 없습니다.")
        return
    except subprocess.CalledProcessError as e:
        stop_event.set()
        progress_thread.join()
        print("\n스크린샷 생성 중 오류 발생:")
        print(e.stderr)
        return

    images = [img for img in sorted(os.listdir(screenshots_dir)) if img.endswith(".png")]
    if not images:
        print("스크린샷이 없어 PDF를 생성할 수 없습니다.")
        return

    print(f"\n'{pdf_path}' 이름으로 PDF 파일 생성을 시작합니다...")
    
    # PDF 생성 프로그레스 인디케이터 시작
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_indicator, args=("PDF 생성 중", stop_event))
    progress_thread.start()
    
    pil_images = []
    for img_file in images:
        img_path = os.path.join(screenshots_dir, img_file)
        pil_images.append(Image.open(img_path).convert('RGB'))

    if pil_images:
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
        stop_event.set()
        progress_thread.join()
        print("PDF 생성 완료!")

def create_readme(video_info, url, download_folder, interval_seconds):
    """README.md 파일을 생성하여 영상 정보를 저장합니다."""
    readme_path = os.path.join(download_folder, 'README.md')
    
    # 시간 정보 포맷팅
    duration_str = "알 수 없음"
    if video_info.get('duration'):
        duration = video_info['duration']
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{int(minutes):02d}:{int(seconds):02d}"
    
    upload_date_str = "알 수 없음"
    if video_info.get('upload_date'):
        upload_date = video_info['upload_date']
        try:
            formatted_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%Y년 %m월 %d일')
            upload_date_str = formatted_date
        except ValueError:
            upload_date_str = upload_date
    
    # 조회수 포맷팅
    view_count_str = "알 수 없음"
    if video_info.get('view_count'):
        view_count = video_info['view_count']
        if view_count >= 1000000:
            view_count_str = f"{view_count/1000000:.1f}M"
        elif view_count >= 1000:
            view_count_str = f"{view_count/1000:.1f}K"
        else:
            view_count_str = str(view_count)
    
    # README 내용 생성
    readme_content = f"""# {video_info.get('title', '제목 없음')}

## 📺 영상 정보
- **원본 URL**: {url}
- **채널명**: {video_info.get('uploader', '알 수 없음')}
- **업로드 날짜**: {upload_date_str}
- **영상 길이**: {duration_str}
- **조회수**: {view_count_str}
- **영상 ID**: {video_info.get('id', '알 수 없음')}

## 📝 설명
{video_info.get('description', '설명이 없습니다.')[:500]}{"..." if len(video_info.get('description', '')) > 500 else ""}

## 📸 스크린샷 정보
- **추출 간격**: {interval_seconds}초마다
- **다운로드 날짜**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}

## 📁 파일 구조
```
{os.path.basename(download_folder)}/
├── README.md (이 파일)
├── {video_info.get('title', '영상파일')}.{video_info.get('ext', 'mp4')}
├── {video_info.get('title', '영상파일')}_screenshots.pdf
└── screenshots/
    ├── screenshot_0001.png
    ├── screenshot_0002.png
    └── ...
```

---
*YouTube Downloader로 생성됨*
"""
    
    # README.md 파일 저장
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"README.md 파일이 생성되었습니다: {readme_path}")
    except Exception as e:
        print(f"README.md 생성 중 오류 발생: {e}")

def main():
    """메인 함수"""
    youtube_url = input("유튜브 URL을 입력하세요: ")
    
    interval_seconds = 0
    while True:
        try:
            interval_str = input("몇 초 간격으로 스크린샷을 추출하시겠습니까? ")
            interval_seconds = int(interval_str)
            if interval_seconds > 0:
                break
            else:
                print("0보다 큰 숫자를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해야 합니다.")

    video_info = get_video_info(youtube_url)
    if not video_info:
        return

    formats = video_info.get('formats', [])
    video_title = video_info.get('title', 'youtube_video')
    duration = video_info.get('duration')

    display_list = display_formats(formats, duration, interval_seconds)
    if not display_list:
        print("다운로드 가능한 비디오 포맷을 찾을 수 없습니다.")
        return

    # 포맷이 1개면 자동으로 선택
    if len(display_list) == 1:
        print("\n사용 가능한 비디오 포맷이 1개이므로 자동으로 선택합니다.")
        selected_format_id = display_list[0]['id']
        downloaded_video_path = download_video(youtube_url, selected_format_id, video_title)
        
        if downloaded_video_path:
            # README.md 생성
            download_folder = os.path.dirname(downloaded_video_path)
            create_readme(video_info, youtube_url, download_folder, interval_seconds)
            # 스크린샷 및 PDF 생성
            take_screenshots_and_create_pdf(downloaded_video_path, interval_seconds)
    else:
        # 포맷이 여러개면 사용자 선택
        while True:
            choice_input = input("다운로드할 포맷의 번호를 선택하세요 (취소하려면 'q' 입력): ")
            if choice_input.lower() == 'q':
                print("작업을 취소합니다.")
                return
            
            try:
                choice = int(choice_input) - 1
                if 0 <= choice < len(display_list):
                    selected_format_id = display_list[choice]['id']
                    downloaded_video_path = download_video(youtube_url, selected_format_id, video_title)
                    
                    if downloaded_video_path:
                        # README.md 생성
                        download_folder = os.path.dirname(downloaded_video_path)
                        create_readme(video_info, youtube_url, download_folder, interval_seconds)
                        # 스크린샷 및 PDF 생성
                        take_screenshots_and_create_pdf(downloaded_video_path, interval_seconds)
                    break
                else:
                    print("잘못된 번호입니다. 목록에 있는 번호를 입력해주세요.")
            except ValueError:
                print("숫자를 입력하거나 'q'를 입력해야 합니다.")

if __name__ == "__main__":
    main()