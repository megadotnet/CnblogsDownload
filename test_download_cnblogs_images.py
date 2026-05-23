import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from bs4 import BeautifulSoup

# We import the functions we want to test from the script
from download_cnblogs_images import (
    sanitize_filename,
    get_article_content,
    extract_article_info,
    extract_images,
    download_image,
)

class TestSanitizeFilename:
    @pytest.mark.parametrize("filename, expected", [
        ("NormalFilename123", "NormalFilename123"),  # Normal filename
        ("File<Name>", "File_Name_"),               # Illegal characters
        ("File:Name", "File_Name"),                 # Illegal characters
        ("File\"Name\"", "File_Name_"),             # Illegal characters
        ("File/Name\\", "File_Name_"),              # Illegal characters
        ("File|Name?", "File_Name_"),               # Illegal characters
        ("File*Name", "File_Name"),                 # Illegal characters
        ("  Spaces Around  ", "Spaces Around"),     # Leading/trailing spaces
        ("...Dots Around...", "Dots Around"),       # Leading/trailing dots
        ("A" * 250, "A" * 200),                     # Max length (200 characters)
    ])
    def test_sanitize_filename(self, filename, expected):
        """Test sanitize_filename with different combinations of characters and lengths."""
        assert sanitize_filename(filename) == expected


class TestGetArticleContent:
    @patch('download_cnblogs_images.requests.get')
    def test_get_article_content_success(self, mock_get):
        """Test successful retrieval of article content."""
        mock_response = MagicMock()
        mock_response.text = "<html><body>Hello</body></html>"
        mock_response.apparent_encoding = "utf-8"
        mock_get.return_value = mock_response

        # Act
        result = get_article_content("http://example.com")

        # Assert
        assert result == "<html><body>Hello</body></html>"
        mock_get.assert_called_once_with(
            "http://example.com",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30
        )
        mock_response.raise_for_status.assert_called_once()
        assert mock_response.encoding == "utf-8"

    @patch('download_cnblogs_images.requests.get')
    def test_get_article_content_failure(self, mock_get, capsys):
        """Test failure during retrieval of article content."""
        import requests
        mock_get.side_effect = requests.RequestException("Connection error")

        # Act
        result = get_article_content("http://example.com")

        # Assert
        assert result is None
        captured = capsys.readouterr()
        assert "获取网页失败: Connection error" in captured.out


class TestExtractArticleInfo:
    @pytest.mark.parametrize("html, expected_title, expected_content_length", [
        (
            "<html><head><title>My Article - 博客园</title></head><body><h1 class='postTitle'>Real Title</h1><div id='cnblogs_post_body'><p>Content</p></div></body></html>",
            "Real Title",
            len("<div id=\"cnblogs_post_body\"><p>Content</p></div>")
        ),
        (
            "<html><head><title>My Article - 博客园</title></head><body><h1 id='cb_post_title_url'>Second Title</h1><div class='postBody'><p>More Content</p></div></body></html>",
            "Second Title",
            len("<div class=\"postBody\"><p>More Content</p></div>")
        ),
        (
            "<html><head><title>My Title - 博客园 Some Extra</title></head><body><div id='post_body'><p>Content</p></div></body></html>",
            "My Title",
            len("<div id=\"post_body\"><p>Content</p></div>")
        ),
        (
            "<html><body><div class='random'>Content here</div></body></html>",
            "未命名文章",
            len("<html><body><div class=\"random\">Content here</div></body></html>")
        )
    ])
    def test_extract_article_info(self, html, expected_title, expected_content_length):
        """Test extraction of title and content from different HTML structures."""
        title, content = extract_article_info(html)
        assert title == expected_title
        # Checking content length as an approximation of content matching to avoid whitespace issues
        assert len(str(content)) == expected_content_length

    def test_extract_article_info_warning(self, capsys):
        """Test extraction outputs a warning if content area is not found."""
        html = "<html><head><title>My Article</title></head><body>No special div</body></html>"
        title, content = extract_article_info(html)

        assert title == "My Article"
        assert len(str(content)) == len("<html><head><title>My Article</title></head><body>No special div</body></html>")

        captured = capsys.readouterr()
        assert "警告: 未找到文章正文区域，将搜索整个页面的图片" in captured.out


class TestExtractImages:
    def test_extract_images_normal(self):
        """Test extraction of valid images."""
        html = """
        <div id="cnblogs_post_body">
            <img src="http://example.com/image1.jpg">
            <img data-src="/images/image2.png">
            <img data-original="image3.gif">
        </div>
        """
        content = BeautifulSoup(html, 'html.parser')
        base_url = "http://example.com/p/123.html"

        images = extract_images(content, base_url)

        assert len(images) == 3
        assert images[0] == "http://example.com/image1.jpg"
        assert images[1] == "http://example.com/images/image2.png"
        assert images[2] == "http://example.com/p/image3.gif"

    def test_extract_images_skip_patterns(self):
        """Test that images matching skip patterns are ignored."""
        html = """
        <div id="cnblogs_post_body">
            <img src="http://example.com/image1.jpg">
            <img src="http://example.com/my_avatar.png">
            <img src="http://example.com/icon_small.gif">
            <img src="http://example.com/site_logo.webp">
            <img src="http://example.com/click_button.jpg">
            <img src="http://example.com/image_thumb_thumb.jpg">
        </div>
        """
        content = BeautifulSoup(html, 'html.parser')
        base_url = "http://example.com"

        images = extract_images(content, base_url)

        assert len(images) == 1
        assert images[0] == "http://example.com/image1.jpg"

    def test_extract_images_no_src(self):
        """Test extraction ignores images without source attributes."""
        html = """
        <div id="cnblogs_post_body">
            <img>
            <img alt="Just an alt">
        </div>
        """
        content = BeautifulSoup(html, 'html.parser')
        base_url = "http://example.com"

        images = extract_images(content, base_url)

        assert len(images) == 0


class TestDownloadImage:
    @patch('download_cnblogs_images.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_image_success_with_ext(self, mock_file, mock_get):
        """Test successful image download where URL has an extension."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_get.return_value = mock_response

        # Act
        success, filepath = download_image("http://example.com/image.png", "my_dir/image")

        # Assert
        assert success is True
        assert filepath == "my_dir/image.png"
        mock_get.assert_called_once_with(
            "http://example.com/image.png",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.cnblogs.com/'
            },
            timeout=30,
            stream=True
        )
        mock_response.raise_for_status.assert_called_once()
        mock_file.assert_called_once_with("my_dir/image.png", 'wb')
        mock_file().write.assert_any_call(b"chunk1")
        mock_file().write.assert_any_call(b"chunk2")

    @pytest.mark.parametrize("content_type, expected_ext", [
        ("image/jpeg", ".jpg"),
        ("image/png", ".png"),
        ("image/gif", ".gif"),
        ("image/webp", ".webp"),
        ("text/html", ".jpg"),  # Default fallback
    ])
    @patch('download_cnblogs_images.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_image_success_infer_ext(self, mock_file, mock_get, content_type, expected_ext):
        """Test successful image download where extension is inferred from Content-Type."""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': content_type}
        mock_response.iter_content.return_value = [b"data"]
        mock_get.return_value = mock_response

        # Act
        success, filepath = download_image("http://example.com/image", "my_dir/image")

        # Assert
        assert success is True
        assert filepath == f"my_dir/image{expected_ext}"
        mock_file.assert_called_once_with(f"my_dir/image{expected_ext}", 'wb')

    @patch('download_cnblogs_images.requests.get')
    def test_download_image_failure(self, mock_get, capsys):
        """Test image download failure due to network error."""
        import requests
        mock_get.side_effect = requests.RequestException("Download error")

        # Act
        success, filepath = download_image("http://example.com/image.png", "my_dir/image.png")

        # Assert
        assert success is False
        assert filepath is None

        captured = capsys.readouterr()
        assert "下载图片失败 http://example.com/image.png: Download error" in captured.out


class TestMain:
    @patch('sys.argv', ['download_cnblogs_images.py', 'invalid_url'])
    def test_main_invalid_url(self, capsys):
        """Test main function with an invalid URL formatting."""
        from download_cnblogs_images import main
        import sys

        with pytest.raises(SystemExit) as e:
            main()

        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "错误: URL格式不正确" in captured.out

    @patch('sys.argv', ['download_cnblogs_images.py', 'http://example.com/p/123.html'])
    @patch('download_cnblogs_images.get_article_content', return_value=None)
    def test_main_no_html(self, mock_get_content, capsys):
        """Test main function when get_article_content returns None."""
        from download_cnblogs_images import main

        main()

        captured = capsys.readouterr()
        assert "无法获取网页内容，程序退出" in captured.out

    @patch('sys.argv', ['download_cnblogs_images.py', 'http://example.com/p/123.html'])
    @patch('download_cnblogs_images.get_article_content', return_value="<html></html>")
    @patch('download_cnblogs_images.extract_article_info')
    @patch('download_cnblogs_images.extract_images', return_value=[])
    def test_main_no_images(self, mock_extract_images, mock_extract_info, mock_get_content, capsys):
        """Test main function when no images are found."""
        from download_cnblogs_images import main

        mock_extract_info.return_value = ("Test Title", "Mock Content")

        main()

        captured = capsys.readouterr()
        assert "未找到图片，程序退出" in captured.out

    @patch('sys.argv', ['download_cnblogs_images.py', 'http://example.com/p/123.html'])
    @patch('download_cnblogs_images.get_article_content', return_value="<html></html>")
    @patch('download_cnblogs_images.extract_article_info')
    @patch('download_cnblogs_images.extract_images', return_value=["http://example.com/image1.jpg", "http://example.com/image2.png"])
    @patch('download_cnblogs_images.download_image')
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('time.sleep')
    def test_main_success(self, mock_sleep, mock_makedirs, mock_exists, mock_download_image, mock_extract_images, mock_extract_info, mock_get_content, capsys):
        """Test a complete successful run of the main function."""
        from download_cnblogs_images import main

        mock_extract_info.return_value = ("Test Title", "Mock Content")
        mock_download_image.side_effect = [
            (True, "Test Title/Test Title_0.jpg"),
            (False, None)
        ]

        main()

        mock_makedirs.assert_called_once_with("Test Title")
        assert mock_download_image.call_count == 2
        assert mock_sleep.call_count == 2

        captured = capsys.readouterr()
        assert "图片保存在目录: Test Title" in captured.out
        assert "成功: 1/2" in captured.out
