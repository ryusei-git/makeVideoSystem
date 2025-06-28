# 参考 https://note.com/diy_smile/n/n5ded99a62cb0
from yt_dlp import YoutubeDL
import os

"""
@param : time_str (str): "HH:MM:SS" 形式の時間文字列。
@return : int: 秒数に変換された整数値。
"""
def time_to_seconds(time_str):
    try:
        # "HH:MM:SS" 形式でない場合は ValueError を発生させる
        if not isinstance(time_str, str) or len(time_str.split(':')) != 3:
            raise ValueError("Time string must be in 'HH:MM:SS' format.")
        else :
            # "HH:MM:SS" 形式に分割して整数に変換
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        
    except ValueError as e:
        print(f"Error: {e}")
        return 0


def ytdlp_bytime(movie_url: str, time_ranges: list):
    for idx, (start, end) in enumerate(time_ranges, start=1):
        # download_sectionsの形式: "*start-end"
        section = f"*{start}-{end}"
        ydl_opts = {
            'outtmpl': os.path.join('base_videos', f'video_{idx}_{start}-{end}.%(ext)s'),
            'download_sections': section
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([movie_url])

def main():
    movie_url = 'https://youtu.be/6olH7m-OJXM'
    # 時間範囲を複数設定
    time_ranges = [
        ('00:01:30', '00:02:21')
    ]

    ytdlp_bytime(movie_url, time_ranges)

if __name__ == "__main__":
    main()