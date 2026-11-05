# AI News Summarizer

以 Python 命令列程式呼叫本機 Ollama，將貼上的新聞整理為繁體中文標題、三個重點及 100 字以內的摘要。

## 準備環境

需要 Python 3.12 以上、[uv](https://docs.astral.sh/uv/) 及 [Ollama](https://ollama.com/download)。
在專案目錄執行：

```bash
uv sync
ollama pull qwen2.5:3b
```

啟動 Ollama 應用程式，或在另一個終端機執行 `ollama serve`。若應用程式已在執行，不必重複啟動服務。
第一次下載模型需要網路及磁碟空間；下載完成後，摘要透過本機 `http://localhost:11434/api/generate` 產生，不需要 API 金鑰。

## 執行

```bash
uv run ai-news-summarizer
```

貼上新聞，可包含多行及空白行，最後輸入單獨一行 `/end` 並按 Enter：

```text
請貼上新聞內容，完成後輸入單獨一行 /end：
某公司今天公布新的人工智慧模型，並開放研究人員試用。
該公司表示將於下個月公布評測結果。
/end
```

程式會顯示新聞標題、編號 1 到 3 的重點與摘要。也可使用已下載的其他本機模型：

```bash
ollama pull qwen2.5:7b
uv run ai-news-summarizer --model qwen2.5:7b
```

按 Ctrl+C 取消。輸入結束也可使用 EOF（macOS/Linux 為 Ctrl+D；Windows 為 Ctrl+Z 後按 Enter）。

## 錯誤處理

- 無法連線或逾時：確認已安裝並啟動 Ollama；每次請求的連線／讀取逾時為 180 秒。
- 找不到模型：依提示執行 `ollama pull 模型名稱`，用 `ollama list` 檢查已下載模型。
- 模型執行失敗：檢查 Ollama 錯誤訊息及電腦可用記憶體，可改用較小模型。
- 回覆格式不符：程式會自動重試一次；仍失敗時，請重新執行或更換模型。程式會檢查標題非空、恰好三個非空重點及摘要長度。連線或 HTTP 錯誤不會自動重試。
- 空白新聞：請提供內容後再試。錯誤時程式會以狀態碼 1 結束。

摘要的 100 字限制以 Python `len()` 計算，包含標點及空白。程式使用 Ollama JSON Schema 約束欄位，並將 `temperature` 設為 0 以降低輸出隨機性。提示詞要求保留原文的日期、數字、名稱與不確定語氣，例如「下月」不得改為「三月」。這些措施無法保證事實正確，請仍對照原文；繁體中文要求由提示詞引導，程式不會自動轉換字體。

### macOS：找不到專案套件

若 `uv sync` 後仍出現 `ModuleNotFoundError: No module named 'ai_news_summarizer'`，可先執行：

```bash
uv sync --reinstall-package ai-news-summarizer
uv run ai-news-summarizer --help
```

若仍失敗，檢查 `.venv/lib/python3.12/site-packages/` 裡本專案的 `.pth` 檔是否帶有 macOS `hidden` 旗標（可用 `ls -lO` 查看）。Python 會略過被標記為隱藏的 `.pth` 檔；確認檔名後，使用 `chflags nohidden 檔案路徑` 清除該檔旗標，再重新執行。虛擬環境的 Python 版本不同時，路徑也需調整。

若系統持續重新加上隱藏旗標，可以改用不依賴 `.pth` 的一般套件安裝方式：

```bash
uv run --no-editable ai-news-summarizer
```

此模式會將程式複製進虛擬環境；修改原始碼後，可用 `uv run --no-editable --reinstall-package ai-news-summarizer ai-news-summarizer` 重新安裝並執行。正常環境仍使用原本的 `uv run ai-news-summarizer` 即可。

## 測試

```bash
uv run python -m unittest discover -s tests -v
```

使用標準函式庫 `unittest` 與 mock，測試不需要安裝或啟動 Ollama，也不會下載模型。
程式只使用 Python 標準函式庫，不需要額外依賴。

## 檔案結構

```text
pyproject.toml                       # uv 專案設定與命令列入口
uv.lock                              # uv 鎖定檔
src/ai_news_summarizer/__init__.py    # 輸入、Ollama 呼叫及輸出
tests/test_summarizer.py              # mock 測試
```

Ollama 呼叫格式參考[官方 Generate API 文件](https://docs.ollama.com/api/generate)。

## 靜態展示網站與 GitHub Pages

`docs/index.html` 與 `docs/style.css` 提供繁體中文專案介紹、技術架構、使用步驟及靜態摘要範例，支援手機與電腦。直接用瀏覽器開啟 `docs/index.html` 即可在本機查看，不需建置或安裝前端依賴。

網站中的新聞為虛構示例，摘要為預先撰寫的靜態內容。網站不會執行 Python、連線 Ollama 或即時生成摘要；實際摘要請依上述步驟在本機執行命令列程式。網站沒有外部後端、API 金鑰或付費服務。

準備部署時，請自行將 `docs/` 檔案提交並推送至 GitHub 的 `main` 分支，再依序設定：

1. 開啟 [GitHub Repository](https://github.com/Ycc1519/ai-news-summarizer)。
2. 進入 **Settings > Pages**。
3. 在 **Build and deployment > Source** 選擇 **Deploy from a branch**。
4. 在 **Branch** 選擇 **main**，資料夾選擇 **/docs**。
5. 按下 **Save**，等待 GitHub Pages 部署完成。
6. 在 Pages 設定頁查看網站網址，或到 **Actions** 查看 Pages 部署結果；成功後開啟網址確認頁面與樣式正常。

預期網站網址為 <https://Ycc1519.github.io/ai-news-summarizer/>；實際部署狀態與網址以 Pages 設定頁為準。之後推送 `main` 分支中的 `docs/` 更新，GitHub Pages 就會重新部署。此設定不需修改既有的 `.github/workflows/tests.yml`。

部署操作參考 [GitHub Pages 官方說明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。
