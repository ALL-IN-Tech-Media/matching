#!/usr/bin/env python3
"""
下载指定的TikTok视频
URL: https://www.tiktok.com/@theinternationalkid/video/7510348663663709447?is_from_webapp=1&sender_device=pc
"""

import os
import requests
import time

# 设置代理环境变量
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

def download_video():
    """下载指定的TikTok视频"""
    
    url = "https://www.tiktok.com/@allianadolina/video/7530178087099616520"
    video_id = "7510348663663709447"
    output_filename = f"tiktok_{video_id}.mp4"
    
    print(f"开始下载视频: {url}")
    print(f"视频ID: {video_id}")
    print(f"输出文件: {output_filename}")
    print(f"使用代理: {os.environ.get('http_proxy')}")
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }
    
    # 设置代理
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    try:
        print("1. 尝试直接访问TikTok页面...")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        
        if response.status_code == 200:
            print("✅ 页面访问成功")
            content = response.text
            
            # 保存页面内容用于调试
            with open('tiktok_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("页面内容已保存到 tiktok_page.html")
            
            # 尝试提取视频信息
            import re
            
            # 查找视频相关的JSON数据
            json_patterns = [
                r'<script id="SIGI_STATE" type="application/json">(.*?)</script>',
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                r'"video":{"urls":\["([^"]+)"',
                r'"downloadAddr":"([^"]+)"',
                r'"playAddr":"([^"]+)"',
            ]
            
            video_url = None
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"找到匹配: {pattern}")
                    if pattern.startswith('"video"'):
                        video_url = matches[0].replace('\\u002F', '/')
                        break
                    else:
                        # 尝试解析JSON
                        try:
                            import json
                            json_data = json.loads(matches[0])
                            print(f"JSON数据: {json_data}")
                        except:
                            print("JSON解析失败")
            
            if video_url:
                print(f"找到视频URL: {video_url}")
                
                # 下载视频
                print("2. 开始下载视频...")
                video_response = requests.get(video_url, headers=headers, proxies=proxies, timeout=60, stream=True)
                
                if video_response.status_code == 200:
                    total_size = int(video_response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(output_filename, 'wb') as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
                    
                    print(f"\n✅ 视频下载成功: {output_filename}")
                    return True
                else:
                    print(f"❌ 视频下载失败，状态码: {video_response.status_code}")
            else:
                print("❌ 未找到视频URL")
        
        else:
            print(f"❌ 页面访问失败，状态码: {response.status_code}")
        
        # 尝试使用yt-dlp
        print("3. 尝试使用yt-dlp...")
        try:
            import subprocess
            
            cmd = [
                'yt-dlp',
                '--proxy', 'http://127.0.0.1:7890',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-o', output_filename,
                url
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ 使用yt-dlp下载成功: {output_filename}")
                return True
            else:
                print(f"❌ yt-dlp下载失败:")
                print(f"错误输出: {result.stderr}")
                print(f"标准输出: {result.stdout}")
        except FileNotFoundError:
            print("yt-dlp未安装，请先安装: pip install yt-dlp")
        except subprocess.TimeoutExpired:
            print("yt-dlp下载超时")
        except Exception as e:
            print(f"yt-dlp执行错误: {str(e)}")
    
    except Exception as e:
        print(f"❌ 下载过程中出现错误: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = download_video()
    
    if success:
        print("🎉 下载完成!")
    else:
        print("❌ 下载失败，请检查网络连接和代理设置")
        print("建议:")
        print("1. 确保代理服务器正在运行")
        print("2. 检查代理端口7890是否可访问")
        print("3. 尝试安装yt-dlp: pip install yt-dlp") 