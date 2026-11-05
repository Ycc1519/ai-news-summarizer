import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from ai_news_summarizer import main, summarize


VALID_RESULT = {
    "title": "AI 新聞",
    "points": ["第一個重點", "第二個重點", "第三個重點"],
    "summary": "這是一段新聞摘要。",
}


def mock_response(result):
    return io.BytesIO(json.dumps({"response": json.dumps(result)}).encode())


class SummarizerTests(unittest.TestCase):
    @patch("ai_news_summarizer.urlopen")
    def test_success_and_request(self, urlopen):
        urlopen.return_value = mock_response(VALID_RESULT)
        self.assertEqual(summarize("新聞內容", "test-model"), VALID_RESULT)
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["prompt"], "新聞內容")
        self.assertFalse(payload["stream"])
        self.assertEqual(request.full_url, "http://localhost:11434/api/generate")

    @patch("ai_news_summarizer.urlopen")
    def test_empty_input(self, urlopen):
        with self.assertRaisesRegex(ValueError, "不可為空白"):
            summarize("  \n")
        urlopen.assert_not_called()

    @patch("ai_news_summarizer.urlopen", side_effect=URLError("refused"))
    def test_connection_error(self, urlopen):
        with self.assertRaisesRegex(ValueError, "ollama serve"):
            summarize("新聞")

    @patch("ai_news_summarizer.urlopen", side_effect=TimeoutError)
    def test_timeout(self, urlopen):
        with self.assertRaisesRegex(ValueError, "逾時"):
            summarize("新聞")

    @patch("ai_news_summarizer.urlopen")
    def test_http_errors(self, urlopen):
        for code, message in [(404, "ollama pull"), (500, "HTTP 500")]:
            with self.subTest(code=code):
                urlopen.side_effect = HTTPError("url", code, "error", {}, None)
                with self.assertRaisesRegex(ValueError, message):
                    summarize("新聞")

    @patch("ai_news_summarizer.urlopen")
    def test_invalid_output(self, urlopen):
        cases = [
            {**VALID_RESULT, "points": ["只有一個"]},
            {**VALID_RESULT, "summary": "字" * 101},
            {**VALID_RESULT, "title": ""},
            {**VALID_RESULT, "points": ["一", "二", 3]},
            {},
        ]
        for result in cases:
            with self.subTest(result=result):
                urlopen.return_value = mock_response(result)
                with self.assertRaisesRegex(ValueError, "格式不符"):
                    summarize("新聞")

    @patch("ai_news_summarizer.urlopen")
    def test_invalid_json(self, urlopen):
        urlopen.return_value = io.BytesIO(b"not json")
        with self.assertRaisesRegex(ValueError, "無法解析"):
            summarize("新聞")

    @patch("sys.argv", ["ai-news-summarizer", "--model", "test-model"])
    @patch("builtins.input", side_effect=["第一行", "", "第二行", "/end"])
    @patch("ai_news_summarizer.summarize", return_value=VALID_RESULT)
    def test_cli_success(self, summarize_mock, input_mock):
        output = io.StringIO()
        with redirect_stdout(output):
            main()
        summarize_mock.assert_called_once_with("第一行\n\n第二行", "test-model")
        self.assertIn("新聞標題：AI 新聞", output.getvalue())
        self.assertIn("3. 第三個重點", output.getvalue())
        self.assertIn("摘要：這是一段新聞摘要。", output.getvalue())

    @patch("sys.argv", ["ai-news-summarizer"])
    @patch("builtins.input", side_effect=EOFError)
    def test_cli_empty_input(self, input_mock):
        error = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(error):
            with self.assertRaises(SystemExit) as exc:
                main()
        self.assertEqual(exc.exception.code, 1)
        self.assertIn("不可為空白", error.getvalue())


if __name__ == "__main__":
    unittest.main()
