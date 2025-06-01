# Discord MCPサーバー（REST API版）

このプロジェクトは、DiscordのBot機能をMCP（Model Context Protocol）ツールとして提供するサーバーです。
REST APIのみを利用し、標準入出力（Stdioトランスポート）でMCPクライアントと通信します。

## 主な機能（ツール）

- `send_message`：指定したチャンネルにメッセージを送信
- `get_server_info`：サーバー情報の取得
- `list_members`：サーバーメンバー一覧とロール名の取得
- `get_user_info`：ユーザー情報の取得
- `get_roles`：サーバー内のロール一覧取得

## セットアップ手順

### 1. Discord Botの作成
- [Discord Developer Portal](https://discord.com/developers/applications) で新規アプリケーションを作成
- Botを作成し、トークンを取得
- Botをサーバーに招待（必要な権限を付与）

### 2. 必要な環境変数
- `DISCORD_TOKEN`：Botのトークン
- `DISCORD_GUILD_ID`：サーバーID（ギルドID）

例：
```bash
export DISCORD_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export DISCORD_GUILD_ID=123456789012345678
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. サーバーの起動
```bash
python src/discord_mcp/rest_api_sample.py
```

MCPクライアントからStdioトランスポートで接続してください。

## ログについて
- すべてのAPIリクエストやMCPツール呼び出しのログは `/tmp/discord_mcp_rest_api.log` に出力されます。
- 問題発生時はこのファイルを確認してください。

## 注意事項
- 本サーバーはREST APIのみを利用しているため、Bot Gatewayイベントには対応していません。
- チャンネルIDは都度ツール呼び出し時に指定してください（環境変数不要）。

## ライセンス
MIT License
