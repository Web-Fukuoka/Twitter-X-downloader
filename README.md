# Twitter（X）downloader

ツイートのURLを渡すだけで動画を保存するツールです。中身は [yt-dlp](https://github.com/yt-dlp/yt-dlp) を使っています。

## 0. スマホ用Webページで使う(おすすめ)

1. このリポジトリを自分のGitHubに置く
2. **Settings → Pages** で Source を「Deploy from a branch」、Branch を `main` / `(root)` にして保存
3. 数分後に `https://ユーザー名.github.io/リポジトリ名/` が開けるようになります(ホーム画面に追加すると便利)
4. 初回だけトークンを設定:
   [トークン作成ページ](https://github.com/settings/personal-access-tokens/new)で
   「Only select repositories」→このリポジトリ、Permissions の **Actions: Read and write** にして作成し、ページに貼る
5. あとはURLを貼って「ダウンロード」→ 完了したら動画を再生・「保存」で共有シートから写真に保存

> GitHub Pages は無料プランだと Public リポジトリのみです。Public の場合、ダウンロードした動画(Artifacts)は他のGitHubユーザーからも見えるので注意してください。

## 1. GitHub上で使う(インストール不要・スマホからもOK)

1. このリポジトリを自分のGitHubに置く(Fork か新規リポジトリにアップロード)
2. **Actions** タブ →「Twitter動画をダウンロード」→ **Run workflow**
3. ツイートのURLを貼って実行
4. 完了したら実行結果のページ下部の **Artifacts** から `twitter-videos` をダウンロード(zip、7日間保存)

> 公開リポジトリだとArtifactsは他の人からも見えます。気になる場合は **Private** リポジトリにしてください。

### ログインが必要な動画(センシティブ設定など)
ブラウザ拡張などでログイン中の `cookies.txt` を書き出し、その中身を
**Settings → Secrets and variables → Actions → New repository secret** に
名前 `TWITTER_COOKIES` で登録してください。

## 2. 自分のPCで使う

```bash
pip install -r requirements.txt
python twdl.py https://x.com/user/status/1234567890      # コマンドライン
python twdl.py -o 保存先 URL1 URL2                        # 複数・保存先指定
python twdl.py                                           # GUIで起動
```

[ffmpeg](https://ffmpeg.org/) が入っていると最高画質で保存されます(なくても動きます)。

## うまくいかないとき
- `pip install -U yt-dlp` で更新(Twitter側の仕様変更に追従するため)
- 鍵アカウント・センシティブ動画はCookieが必要

## 注意
ダウンロードした動画の著作権は投稿者にあります。個人での視聴・保存の範囲で使い、無断転載はしないでください。
