#!/usr/bin/env python3
"""
Twitter（X）downloader

使い方:
  python twdl.py <URL> [<URL> ...]        # コマンドラインで保存
  python twdl.py -o downloads <URL>       # 保存先フォルダを指定
  python twdl.py --gui                    # GUIで起動 (引数なしでもGUI)

必要なもの: pip install -r requirements.txt  (yt-dlp)
音声と映像を結合するために ffmpeg があると最高画質で保存できます。
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp が見つかりません。`pip install -r requirements.txt` を実行してください。")

URL_RE = re.compile(r"^https?://(www\.|mobile\.)?(twitter\.com|x\.com)/[^/]+/status/\d+", re.I)


def normalize_url(url: str) -> str:
    """x.com / mobile.twitter.com などを含むURLを整形する"""
    url = url.strip()
    url = url.split("?")[0]
    return url


def is_valid_url(url: str) -> bool:
    return bool(URL_RE.match(url))


def download(urls, out_dir="downloads", cookies=None, log=print):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    has_ffmpeg = shutil.which("ffmpeg") is not None
    opts = {
        "outtmpl": str(out / "%(uploader_id)s_%(id)s_%(autonumber)s.%(ext)s"),
        # ffmpeg があれば最高画質+音声を結合、なければ結合済みの最良形式
        "format": "bestvideo+bestaudio/best" if has_ffmpeg else "best",
        "merge_output_format": "mp4",
        "noplaylist": False,  # 1ツイートに複数動画がある場合も全部保存
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: _progress(d, log)],
    }
    if cookies:
        # センシティブ設定・非公開アカウントの動画にはログイン済みCookieが必要
        opts["cookiefile"] = cookies

    saved, failed = [], []
    with yt_dlp.YoutubeDL(opts) as ydl:
        for raw in urls:
            url = normalize_url(raw)
            if not is_valid_url(url):
                log(f"[スキップ] ツイートのURLではありません: {raw}")
                failed.append(raw)
                continue
            log(f"[取得中] {url}")
            try:
                ydl.download([url])
                saved.append(url)
            except yt_dlp.utils.DownloadError as e:
                log(f"[失敗] {url}\n  {e}")
                failed.append(url)

    log(f"\n完了: 成功 {len(saved)} 件 / 失敗 {len(failed)} 件  → 保存先: {out.resolve()}")
    return saved, failed


def _progress(d, log):
    if d["status"] == "finished":
        log(f"  保存: {Path(d['filename']).name}")


def run_gui():
    import threading
    import tkinter as tk
    from tkinter import filedialog, scrolledtext

    root = tk.Tk()
    root.title("Twitter（X）downloader")
    root.geometry("640x420")

    tk.Label(root, text="ツイートのURL(複数ある場合は1行に1つ)").pack(anchor="w", padx=10, pady=(10, 0))
    url_box = tk.Text(root, height=5)
    url_box.pack(fill="x", padx=10)

    row = tk.Frame(root)
    row.pack(fill="x", padx=10, pady=6)
    tk.Label(row, text="保存先:").pack(side="left")
    out_var = tk.StringVar(value=str(Path("downloads").resolve()))
    tk.Entry(row, textvariable=out_var).pack(side="left", fill="x", expand=True, padx=4)
    tk.Button(row, text="参照", command=lambda: out_var.set(filedialog.askdirectory() or out_var.get())).pack(side="left")

    log_box = scrolledtext.ScrolledText(root, height=12, state="disabled")

    def log(msg):
        def _w():
            log_box.configure(state="normal")
            log_box.insert("end", msg + "\n")
            log_box.see("end")
            log_box.configure(state="disabled")
        root.after(0, _w)

    def start():
        urls = [u for u in url_box.get("1.0", "end").split() if u.strip()]
        if not urls:
            log("URLを入力してください。")
            return
        btn.configure(state="disabled")

        def work():
            try:
                download(urls, out_var.get(), log=log)
            finally:
                root.after(0, lambda: btn.configure(state="normal"))

        threading.Thread(target=work, daemon=True).start()

    btn = tk.Button(root, text="ダウンロード", command=start)
    btn.pack(pady=4)
    log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    root.mainloop()


def main():
    p = argparse.ArgumentParser(description="Twitter(X)の動画をURLからダウンロード")
    p.add_argument("urls", nargs="*", help="ツイートのURL")
    p.add_argument("-o", "--output", default="downloads", help="保存先フォルダ (既定: downloads)")
    p.add_argument("-c", "--cookies", help="cookies.txt のパス (ログインが必要な動画用)")
    p.add_argument("--gui", action="store_true", help="GUIで起動")
    a = p.parse_args()

    if a.gui or not a.urls:
        try:
            run_gui()
        except Exception as e:  # tkinter がない環境(サーバー等)
            p.print_help()
            sys.exit(f"\nGUIを起動できませんでした ({e})。URLを引数に指定してください。")
        return

    _, failed = download(a.urls, a.output, a.cookies)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
