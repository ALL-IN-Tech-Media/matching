服务端启动：
gunicorn -w 1 -b 0.0.0.0:5000 matching.video_to_text_server:app --timeout 600

服务器视频下载（国内服务器需要vpn）：
sudo ./clash -d .（clash和配置文件在同一路径下）
python download_specific_video.py
实质上是用cmd = [
                'yt-dlp',
                '--proxy', 'http://127.0.0.1:7890',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-o', output_filename,
                url
            ]
从url下载视频到服务器本地

11条视频内容分析用例：
python batch_curl_requests.py
结果存储在batch_results.json中

