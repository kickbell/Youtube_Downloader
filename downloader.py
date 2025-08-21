import os
import subprocess
import json
import shutil
import time
import threading
from PIL import Image

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
    command = ['yt-dlp', '-j', url]
    
    # 프로그레스 인디케이터 시작
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_indicator, args=("정보를 가져오는 중", stop_event))
    progress_thread.start()
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        stop_event.set()
        progress_thread.join()
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        stop_event.set()
        progress_thread.join()
        print(f"\r오류: 비디오 정보를 가져올 수 없습니다. URL을 확인하세요.")
        print(e.stderr)
        return None
    except json.JSONDecodeError:
        stop_event.set()
        progress_thread.join()
        print("\r오류: 비디오 정보 파싱에 실패했습니다.")
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

    print("-" * 80)
    print("{:<4} {:<9} {:<14} {:<19} {:<24}".format("번호", "해상도", "파일(예상)", "PDF(예상)", "코덱"))
    print("-" * 80)

    display_list = []
    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
            filesize = f.get('filesize') or f.get('filesize_approx')
            filesize_str = f"{filesize / 1024 / 1024:.2f} MB" if filesize else "N/A"
            
            display_list.append({
                'id': f['format_id'],
                'resolution': f.get('resolution', 'N/A'),
                'filesize': filesize_str,
                'vcodec': f.get('vcodec', 'N/A')
            })

    for i, item in enumerate(display_list):
        print("{:<5} {:<12} {:<18} {:<22} {:<15}".format(
            i + 1, item['resolution'], item['filesize'], estimated_pdf_size_str, item['vcodec']
        ))
    
    print("-" * 80)
    return display_list

def download_video(url, format_id, video_title):
    """선택한 포맷으로 비디오를 다운로드하고, 파일 경로를 반환합니다."""
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
    
    # 비디오 정보 가져오기
    info_command = ['yt-dlp', '-j', '-f', format_id, url]
    video_info = json.loads(subprocess.run(info_command, capture_output=True, text=True).stdout)
    ext = video_info.get('ext', 'mp4')
    final_video_path = os.path.join(download_folder, f'{safe_title}.{ext}')

    print(f"\n'{download_folder}' 폴더에 다운로드를 시작합니다...")
    command = ['yt-dlp', '-f', format_id, '-o', output_template, url]
    
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
        print("포맷이 1개뿐이므로 자동으로 선택합니다.")
        selected_format_id = display_list[0]['id']
        downloaded_video_path = download_video(youtube_url, selected_format_id, video_title)
        
        if downloaded_video_path:
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
                        take_screenshots_and_create_pdf(downloaded_video_path, interval_seconds)
                    break
                else:
                    print("잘못된 번호입니다. 목록에 있는 번호를 입력해주세요.")
            except ValueError:
                print("숫자를 입력하거나 'q'를 입력해야 합니다.")

if __name__ == "__main__":
    main()