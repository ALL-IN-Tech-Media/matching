import subprocess
import json
import time
import os

# 基础路径
BASE_PATH = "/media/tangshi/AI001/data/gc"
SERVER_URL = "http://localhost:5000/video_to_text"

def make_curl_request(video_path):
    """发送curl请求到模型服务器"""
    curl_command = [
        "curl", "-X", "POST", SERVER_URL,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"video_path": video_path})
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": f"curl failed: {result.stderr}"}
    except subprocess.TimeoutExpired:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    results = {}
    
    # 逐个处理1.mp4到11.mp4
    for i in range(1, 12):
        video_filename = f"{i}.mp4"
        video_path = os.path.join(BASE_PATH, video_filename)
        
        print(f"Processing {video_filename}...")
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            print(f"File not found: {video_path}")
            results[video_filename] = {"error": "File not found"}
            continue
        
        # 发送请求
        response = make_curl_request(video_path)
        results[video_filename] = response
        
        # 打印结果
        if "result" in response:
            print(f"✓ {video_filename}: {response['result'][:100]}...")
        else:
            print(f"✗ {video_filename}: {response.get('error', 'Unknown error')}")
        
        # 添加延迟，避免请求过于频繁
        time.sleep(2)
    
    # 保存所有结果到JSON文件
    output_file = "batch_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nAll results saved to {output_file}")
    
    # 打印统计信息
    success_count = sum(1 for r in results.values() if "result" in r)
    error_count = len(results) - success_count
    print(f"Success: {success_count}, Errors: {error_count}")

if __name__ == "__main__":
    main() 