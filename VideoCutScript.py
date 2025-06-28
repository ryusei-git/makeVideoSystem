import datetime
import subprocess
import logging
import re
import os
from yt_dlp import YoutubeDL

log_file = os.path.join('D:\\makeVideoSystem', 'video_system.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def main():
    movie_url = 'https://www.youtube.com/watch?v=qny4da8R-G4&t=13s'
    time_ranges = [
        ('00:02:24', '00:02:29'),
        ('00:03:48', '00:03:50')
    ]
    ytdlp_bytime(movie_url, time_ranges)

def ytdlp_bytime(movie_url: str, time_ranges: list):
    
    # 出力ファイルのリスト
    # 各動画のダウンロード後に保存されるファイルパスを格納
    # 例: ['base_videos/YYYYMMDD/download_1.mp4', 'base_videos/YYYYMMDD/download_2.mp4']
    output_files = []
    
    video_title = get_video_title(movie_url)
    
    if not video_title:
        video_title = "video"

    # 保存先ディレクトリの作成
    # ディレクトリは 'base_videos' の下に、今日の日付で作成
    # 例: base_videos/YYYYMMDD
    # 保存先ディレクトリは絶対パスで指定
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    save_dir = os.path.join('base_videos', today_str)
    os.makedirs(save_dir, exist_ok=True)

    if not time_ranges:
        logging.error("時間範囲が提供されていません。")
        return

    # 時間範囲が存在する場合、各範囲ごとに動画をダウンロード
    # 各範囲は ('HH:MM:SS', 'HH:MM:SS') の形式で指定
    # 例: ('00:02:24', '00:02:29')
    # 各動画は 'download_1.mp4', 'download_2.mp4' のように保存される
    # 保存先ディレクトリは絶対パスで指定
    for idx, (start, end) in enumerate(time_ranges, start=1):
        
        def set_download_ranges(info_dict, self):
            start_seconds = time_to_seconds(start)
            end_seconds = time_to_seconds(end)
            return [{'start_time': start_seconds, 'end_time': end_seconds}]
        
        output_path = os.path.join(save_dir, f'download_{idx}')
        
        # youtubeから動画をダウンロードするためのオプションを設定
        # 'outtmpl' は出力ファイルのテンプレートを指定
        # 'download_ranges' はダウンロードする時間範囲を指定するコールバック関数
        # 'format' はダウンロードする動画のフォーマットを指定(最高画質のmp4を選択)
        # 'postprocessors' はダウンロード後の処理を指定
        # 'overwrites' は既存ファイルを強制的に上書きするオプション
        # 出力ファイルは 'base_videos/YYYYMMDD/download_1.mp4', 'base_videos/YYYYMMDD/download_2.mp4' のように保存される
        ydl_opts = {
            'outtmpl': output_path,
            'download_ranges': set_download_ranges,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'overwrites': True
        }
        
        # 動画をダウンロードする
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([movie_url])
        
        if os.path.exists(output_path + ".mp4"):
            # ダウンロードが成功した場合、出力ファイルのリストに追加
            logging.info(f"保存された: {output_path}, 存在: {os.path.exists(output_path + '.mp4')}")
            output_files.append(output_path+".mp4")
            
            # ダウンロードしたファイルを結合
            if output_files:
                concat_mp4_files(output_files, os.path.join('D:\makeVideoSystem\\'+save_dir, f'concat_concat.mp4'))
        else:
            logging.error(f"保存に失敗: {output_path}")
            return
        

def get_video_title(movie_url: str) -> str:
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(movie_url, download=False)
            return escape_filename(info.get('title', ''))
        except Exception as e:
            logging.error(f"タイトル取得エラー: {e}")
            return ""


def escape_filename(filename: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', filename)


def time_to_seconds(time_str):
    try:
        if not isinstance(time_str, str) or len(time_str.split(':')) != 3:
            raise ValueError("Time string must be in 'HH:MM:SS' format.")
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except ValueError as e:
        logging.error(f"Error: {e}")
        return 0


def concat_mp4_files(input_files, output_file):

    list_file = 'D:\makeVideoSystem\concat_list.txt'
    with open(list_file, 'w', encoding='utf-8') as f:
        for file in input_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    cmd = ['ffmpeg', '-y','-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', output_file]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"ffmpegの実行中にエラーが発生しました: {e}")
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == "__main__":
    main()