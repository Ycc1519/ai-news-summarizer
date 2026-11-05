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

- 無法連線或逾時：確認已安裝並啟動 Ollama；本程式最多等待 180 秒。
- 找不到模型：依提示執行 `ollama pull 模型名稱`，用 `ollama list` 檢查已下載模型。
- 模型執行失敗：檢查 Ollama 錯誤訊息及電腦可用記憶體，可改用較小模型。
- 回覆格式不符：重新執行或更換模型。程式會檢查標題非空、恰好三個非空重點及摘要長度。
- 空白新聞：請提供內容後再試。錯誤時程式會以狀態碼 1 結束。

摘要的 100 字限制以 Python `len()` 計算，包含標點及空白。模型輸出仍可能有誤，請對照原文；繁體中文要求由提示詞引導，程式不會自動轉換字體。

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
