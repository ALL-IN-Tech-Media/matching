import requests
import json
import re
import subprocess
import os
from typing import List, Dict, Any

# 全局配置变量
DEFAULT_DOMAIN = "a10f480ce36a.ngrok-free.app"

def get_tiktok_sec_user_id(tiktok_url: str, domain: str = None) -> List[str]:
    """
    通过TikTok URL获取sec_user_id列表
    
    Args:
        tiktok_url (str): TikTok用户URL，如 "https://www.tiktok.com/@llaurakam"
        domain (str): API域名，默认使用全局配置
    
    Returns:
        List[str]: sec_user_id列表
    
    Example:
        >>> get_tiktok_sec_user_id("https://www.tiktok.com/@llaurakam")
        ['MS4wLjABAAAApam1frHEtkg44uN1CQvup5-y3nfaW1_WBrhLPn124OUbl15DlrsNVEWUSjklRq3h']
    """
    try:
        # 使用传入的domain或默认domain
        api_domain = domain or DEFAULT_DOMAIN
        
        # 提取用户名部分（tiktok.com/后面的参数）
        username_match = re.search(r'tiktok\.com/([^?]+)', tiktok_url)
        if not username_match:
            raise ValueError("Invalid TikTok URL format")
        
        # 构建完整的API URL
        api_url = f"https://{api_domain}/api/tiktok/web/get_all_sec_user_id"
        
        # 准备请求数据
        payload = [tiktok_url]
        
        # 发送请求
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get('code') == 200:
            return result.get('data', [])
        else:
            raise Exception(f"API returned error code: {result.get('code')}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def get_tiktok_user_posts(sec_uid: str, cursor: str = "0", count: int = 16, domain: str = None) -> Dict[str, Any]:
    """
    通过secUid获取用户的视频URL列表、头像和签名信息
    
    Args:
        sec_uid (str): 用户的secUid
        cursor (str): 分页游标，默认为"0"
        count (int): 获取数量，默认为16
        domain (str): API域名，默认使用全局配置
    
    Returns:
        Dict[str, Any]: 包含video_urls、avatarLarger、signature等信息的字典
    
    Example:
        >>> get_tiktok_user_posts("MS4wLjABAAAApam1frHEtkg44uN1CQvup5-y3nfaW1_WBrhLPn124OUbl15DlrsNVEWUSjklRq3h")
        {
            "video_urls": ["https://www.tiktok.com/@llaurakam/video/7465340747311631633", ...],
            "avatarLarger": "https://p16-sign-sg.tiktokcdn.com/...",
            "signature": "kul malaysia 🇲🇾\nIG: @llaurakam 💗\n💌 llaurakam.work@gmail.com"
        }
    """
    try:
        # 使用传入的domain或默认domain
        api_domain = domain or DEFAULT_DOMAIN
        
        # 构建API URL
        api_url = f"https://{api_domain}/api/tiktok/web/fetch_user_post_hot_simple"
        
        # 准备请求参数
        params = {
            'secUid': sec_uid,
            'cursor': cursor,
            'count': count,
            'coverFormat': 2
        }
        
        # 发送请求
        headers = {
            'accept': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get('code') == 200:
            data = result.get('data', {})
            return {
                'video_urls': data.get('video_urls', []),
                'avatarLarger': data.get('avatarLarger', ''),
                'signature': data.get('signature', '')
            }
        else:
            raise Exception(f"API returned error code: {result.get('code')}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def download_avatar_image(avatar_url: str, output_dir: str = None, filename: str = None, proxy: str = "http://127.0.0.1:7890") -> str:
    """
    下载并保存头像图片
    
    Args:
        avatar_url (str): 头像图片URL
        output_dir (str): 输出目录，默认为当前目录
        filename (str): 文件名，默认为"avatar.jpg"
        proxy (str): 代理设置，默认为"http://127.0.0.1:7890"
    
    Returns:
        str: 保存的图片文件的绝对路径
    
    Example:
        >>> avatar_url = "https://p16-sign-sg.tiktokcdn.com/..."
        >>> saved_path = download_avatar_image(avatar_url)
        >>> print(saved_path)
        '/path/to/avatar.jpg'
    """
    try:
        # 设置输出目录
        if output_dir is None:
            output_dir = os.getcwd()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置文件名
        if filename is None:
            # 从URL中提取文件扩展名，默认为jpg
            file_ext = os.path.splitext(avatar_url.split('?')[0])[1]
            if not file_ext:
                file_ext = '.jpg'
            filename = f"avatar{file_ext}"
        
        # 构建完整文件路径
        file_path = os.path.join(output_dir, filename)
        
        # 设置代理
        proxies = {
            'http': proxy,
            'https': proxy
        } if proxy else None
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"Downloading avatar from: {avatar_url}")
        
        # 下载图片
        response = requests.get(avatar_url, headers=headers, proxies=proxies, timeout=30)
        response.raise_for_status()
        
        # 保存图片
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        absolute_path = os.path.abspath(file_path)
        print(f"✓ Avatar saved to: {absolute_path}")
        
        return absolute_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download avatar: {str(e)}")
    except Exception as e:
        raise Exception(f"Error saving avatar: {str(e)}")

def download_tiktok_videos(video_urls: List[str], output_dir: str = None, proxy: str = "http://127.0.0.1:7890") -> List[str]:
    """
    使用yt-dlp从TikTok视频URL列表下载视频
    
    Args:
        video_urls (List[str]): TikTok视频URL列表
        output_dir (str): 输出目录，默认为当前目录
        proxy (str): 代理设置，默认为"http://127.0.0.1:7890"
    
    Returns:
        List[str]: 下载成功的视频文件的绝对路径列表
    
    Example:
        >>> urls = ["https://www.tiktok.com/@user/video/1234567890"]
        >>> downloaded_files = download_tiktok_videos(urls)
        >>> print(downloaded_files)
        ['/path/to/video1.mp4', '/path/to/video2.mp4']
    """
    downloaded_files = []
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.getcwd()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(video_urls):
        try:
            print(f"Downloading video {i+1}/{len(video_urls)}: {url}")
            
            # 构建输出文件名
            output_filename = os.path.join(output_dir, f"tiktok_video_{i+1}.%(ext)s")
            
            # 构建yt-dlp命令
            cmd = [
                'yt-dlp',
                '--proxy', proxy,
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-o', output_filename,
                url
            ]
            
            # 执行下载命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # 查找下载的文件
                for file in os.listdir(output_dir):
                    if file.startswith(f"tiktok_video_{i+1}.") and file.endswith(('.mp4', '.webm', '.mkv')):
                        file_path = os.path.join(output_dir, file)
                        downloaded_files.append(os.path.abspath(file_path))
                        print(f"✓ Successfully downloaded: {file}")
                        break
                else:
                    print(f"⚠ Warning: Could not find downloaded file for video {i+1}")
            else:
                print(f"✗ Failed to download video {i+1}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout downloading video {i+1}")
        except Exception as e:
            print(f"✗ Error downloading video {i+1}: {str(e)}")
    
    print(f"\nDownload summary: {len(downloaded_files)}/{len(video_urls)} videos downloaded successfully")
    return downloaded_files

def process_tiktok_user(tiktok_url: str, output_dir: str = None, proxy: str = "http://127.0.0.1:7890", domain: str = None) -> Dict[str, Any]:
    """
    综合函数：从TikTok URL开始，获取用户信息并下载所有资源
    
    Args:
        tiktok_url (str): TikTok用户URL，如 "https://www.tiktok.com/@llaurakam"
        output_dir (str): 输出目录，默认为当前目录
        proxy (str): 代理设置，默认为"http://127.0.0.1:7890"
        domain (str): API域名，默认使用全局配置
    
    Returns:
        Dict[str, Any]: 包含以下信息的字典
            - video_paths (List[str]): 下载的视频文件绝对路径列表
            - signature (str): 用户签名/简介
            - avatar_path (str): 头像文件绝对路径
    
    Example:
        >>> result = process_tiktok_user("https://www.tiktok.com/@llaurakam")
        >>> print(result)
        {
            'video_paths': ['/path/to/tiktok_video_1.mp4', '/path/to/tiktok_video_2.mp4'],
            'signature': 'kul malaysia 🇲🇾\nIG: @llaurakam 💗\n💌 llaurakam.work@gmail.com',
            'avatar_path': '/path/to/avatar.jpg'
        }
    """
    try:
        print(f"Processing TikTok user: {tiktok_url}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.getcwd()
        
        # 1. 获取secUid
        print("Step 1: Getting secUid...")
        sec_user_ids = get_tiktok_sec_user_id(tiktok_url, domain)
        if not sec_user_ids:
            raise Exception("No secUid found for the given URL")
        
        sec_uid = sec_user_ids[0]  # 使用第一个secUid
        print(f"✓ SecUid obtained: {sec_uid}")
        
        # 2. 获取用户帖子信息
        print("Step 2: Getting user posts...")
        user_posts = get_tiktok_user_posts(sec_uid, domain=domain)
        video_urls = user_posts.get('video_urls', [])
        avatar_url = user_posts.get('avatarLarger', '')
        signature = user_posts.get('signature', '')
        
        print(f"✓ Found {len(video_urls)} videos")
        print(f"✓ Avatar URL: {avatar_url[:50]}...")
        print(f"✓ Signature: {signature[:50]}...")
        
        # 3. 下载视频
        video_paths = []
        if video_urls:
            print("Step 3: Downloading videos...")
            video_paths = download_tiktok_videos(video_urls, output_dir, proxy)
        else:
            print("⚠ No videos to download")
        
        # 4. 下载头像
        avatar_path = ""
        if avatar_url:
            print("Step 4: Downloading avatar...")
            avatar_path = download_avatar_image(avatar_url, output_dir, proxy=proxy)
        else:
            print("⚠ No avatar to download")
        
        # 5. 返回结果
        result = {
            'video_paths': video_paths,
            'signature': signature,
            'avatar_path': avatar_path
        }
        
        print(f"\n✓ Processing completed successfully!")
        print(f"  - Videos downloaded: {len(video_paths)}")
        print(f"  - Avatar downloaded: {'Yes' if avatar_path else 'No'}")
        print(f"  - Signature length: {len(signature)} characters")
        
        return result
        
    except Exception as e:
        raise Exception(f"Error processing TikTok user: {str(e)}")

def get_tiktok_sec_user_id_batch(tiktok_urls: List[str], domain: str = None) -> Dict[str, List[str]]:
    """
    批量获取多个TikTok URL的sec_user_id
    
    Args:
        tiktok_urls (List[str]): TikTok用户URL列表
        domain (str): API域名，默认使用全局配置
    
    Returns:
        Dict[str, List[str]]: URL到sec_user_id列表的映射
    
    Example:
        >>> urls = ["https://www.tiktok.com/@user1", "https://www.tiktok.com/@user2"]
        >>> get_tiktok_sec_user_id_batch(urls)
        {
            "https://www.tiktok.com/@user1": ["sec_user_id_1"],
            "https://www.tiktok.com/@user2": ["sec_user_id_2"]
        }
    """
    results = {}
    
    for url in tiktok_urls:
        try:
            sec_user_ids = get_tiktok_sec_user_id(url, domain)
            results[url] = sec_user_ids
        except Exception as e:
            results[url] = []
            print(f"Error processing {url}: {str(e)}")
    
    return results

# 测试函数
if __name__ == "__main__":
    # 测试综合函数
    test_url = "https://www.tiktok.com/@lucie_baker"
    try:
        result = process_tiktok_user(test_url)
        print(f"\nComprehensive test result:")
        print(f"Video paths: {result['video_paths']}")
        print(f"Signature: {result['signature']}")
        print(f"Avatar path: {result['avatar_path']}")
    except Exception as e:
        print(f"Comprehensive test error: {str(e)}")
    
 
 