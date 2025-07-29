import requests
import json
import time
from typing import List, Dict, Any

class BatchProcessor:
    def __init__(self, server_url: str = "http://localhost:5000"):
        """
        Initialize the batch processor with server URL.
        
        Args:
            server_url (str): The URL of the video_to_text server
        """
        self.server_url = server_url
        self.session = requests.Session()
    
    def batch_video_to_text(self, video_paths: List[str], prompt: str = None, prompt_id: str = "3", 
                           max_new_tokens: int = 1024) -> List[Dict[str, Any]]:
        """
        Process a list of video paths and return results.
        
        Args:
            video_paths (List[str]): List of video file paths or URLs
            prompt (str, optional): Custom prompt to use for all videos
            prompt_id (str): Prompt ID from prompts.json (default: "3")
            max_new_tokens (int): Maximum tokens to generate (default: 1024)
            
        Returns:
            List[Dict[str, Any]]: List of results with video path and generated text
        """
        results = []
        
        for i, video_path in enumerate(video_paths):
            print(f"Processing video {i+1}/{len(video_paths)}: {video_path}")
            
            try:
                payload = {
                    "video_path": video_path,
                    "max_new_tokens": max_new_tokens
                }
                
                if prompt:
                    payload["prompt"] = prompt
                else:
                    payload["prompt_id"] = prompt_id
                
                response = self.session.post(
                    f"{self.server_url}/video_to_text",
                    json=payload,
                    timeout=300  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        "video_path": video_path,
                        "success": True,
                        "result": result.get("result", ""),
                        "error": None
                    })
                else:
                    error_msg = response.json().get("error", "Unknown error")
                    results.append({
                        "video_path": video_path,
                        "success": False,
                        "result": None,
                        "error": error_msg
                    })
                    
            except Exception as e:
                results.append({
                    "video_path": video_path,
                    "success": False,
                    "result": None,
                    "error": str(e)
                })
            
            # Small delay between requests to avoid overwhelming the server
            time.sleep(1)
        
        return results
    
    def batch_videos_to_text_server(self, video_paths: List[str], prompt: str = None, prompt_id: str = "3", 
                                  max_new_tokens: int = 1024) -> List[Dict[str, Any]]:
        """
        Process a list of video paths using the server's batch endpoint for efficient processing.
        
        Args:
            video_paths (List[str]): List of video file paths or URLs
            prompt (str, optional): Custom prompt to use for all videos
            prompt_id (str): Prompt ID from prompts.json (default: "3")
            max_new_tokens (int): Maximum tokens to generate (default: 1024)
            
        Returns:
            List[Dict[str, Any]]: List of results with video path and generated text
        """
        print(f"Processing {len(video_paths)} videos in batch...")
        
        try:
            payload = {
                "video_paths": video_paths,
                "max_new_tokens": max_new_tokens
            }
            
            if prompt:
                payload["prompt"] = prompt
            else:
                payload["prompt_id"] = prompt_id
            
            response = self.session.post(
                f"{self.server_url}/videos_to_text",
                json=payload,
                timeout=600  # 10 minutes timeout for batch processing
            )
            
            if response.status_code == 200:
                result = response.json()
                server_results = result.get("results", [])
                
                # Convert server results to our standard format
                results = []
                for i, (video_path, server_result) in enumerate(zip(video_paths, server_results)):
                    results.append({
                        "video_path": video_path,
                        "success": True,
                        "result": server_result,
                        "error": None
                    })
                
                print(f"Successfully processed {len(results)} videos")
                return results
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"Batch processing failed: {error_msg}")
                
                # Return error results for all videos
                results = []
                for video_path in video_paths:
                    results.append({
                        "video_path": video_path,
                        "success": False,
                        "result": None,
                        "error": error_msg
                    })
                return results
                
        except Exception as e:
            print(f"Batch processing exception: {str(e)}")
            
            # Return error results for all videos
            results = []
            for video_path in video_paths:
                results.append({
                    "video_path": video_path,
                    "success": False,
                    "result": None,
                    "error": str(e)
                })
            return results
    
    def img_to_text(self, image_path: str, prompt: str = None, prompt_id: str = "0", 
                   max_new_tokens: int = 1024) -> Dict[str, Any]:
        """
        Process a single image path and return result.
        
        Args:
            image_path (str): Image file path or URL
            prompt (str, optional): Custom prompt to use for the image
            prompt_id (str): Prompt ID from prompts.json (default: "0")
            max_new_tokens (int): Maximum tokens to generate (default: 1024)
            
        Returns:
            Dict[str, Any]: Result with image path and generated text
        """
        print(f"Processing image: {image_path}")
        
        try:
            payload = {
                "image_path": image_path,
                "max_new_tokens": max_new_tokens
            }
            
            if prompt:
                payload["prompt"] = prompt
            else:
                payload["prompt_id"] = prompt_id
            
            response = self.session.post(
                f"{self.server_url}/img_to_text",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "image_path": image_path,
                    "success": True,
                    "result": result.get("result", ""),
                    "error": None
                }
            else:
                error_msg = response.json().get("error", "Unknown error")
                return {
                    "image_path": image_path,
                    "success": False,
                    "result": None,
                    "error": error_msg
                }
                
        except Exception as e:
            return {
                "image_path": image_path,
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    def text_to_text_with_prefix(self, text: str, prefix: str = "请分析以下内容并给出详细回答：", 
                                max_new_tokens: int = 1024) -> Dict[str, Any]:
        """
        Process a single text with a fixed prefix.
        
        Args:
            text (str): The text to process
            prefix (str): Fixed prefix to add before the text (default: "请分析以下内容并给出详细回答：")
            max_new_tokens (int): Maximum tokens to generate (default: 1024)
            
        Returns:
            Dict[str, Any]: Result with success status and generated text
        """
        print(f"Processing text with prefix: {prefix[:50]}...")
        
        try:
            # Combine prefix with the input text
            full_prompt = f"{prefix}{text}"
            
            payload = {
                "prompt": full_prompt,
                "max_new_tokens": max_new_tokens
            }
            
            response = self.session.post(
                f"{self.server_url}/text_to_text",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result.get("result", ""),
                    "error": None,
                    "original_text": text,
                    "full_prompt": full_prompt
                }
            else:
                error_msg = response.json().get("error", "Unknown error")
                return {
                    "success": False,
                    "result": None,
                    "error": error_msg,
                    "original_text": text,
                    "full_prompt": full_prompt
                }
                
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e),
                "original_text": text,
                "full_prompt": f"{prefix}{text}"
            }
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """
        Save results to a JSON file.
        
        Args:
            results (List[Dict[str, Any]]): Results to save
            output_file (str): Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Results saved to: {output_file}")


# Example usage
if __name__ == "__main__":
    # Initialize the batch processor
    processor = BatchProcessor()
    
    # Example 1: Batch process videos using the new efficient server endpoint
    video_paths = ['/media/tangshi/AI001/data/gc/matching/tiktok_video_5.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_6.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_7.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_10.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_11.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_12.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_14.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_15.mp4', '/media/tangshi/AI001/data/gc/matching/tiktok_video_16.mp4']
    
    print("=== Processing Videos (Efficient Batch Method) ===")
    video_results = processor.batch_videos_to_text_server(
        video_paths=video_paths,
        prompt="""from these category get three tags for the video:- Lifestyle & Daily Vlog（生活方式 · 日常 Vlog）
- Travel & Adventure（旅游 · 户外探险）
- Gaming & eSports（游戏 · 电竞）
- Comedy & Humor（搞笑 · 幽默）
- Food & Cooking（美食 · 料理）
- Beauty & Makeup（美妆 · 护肤）
- Fashion & Style（时尚 · 穿搭）
- Tech & Gadgets（科技 · 数码评测）
- Fitness & Wellness（运动 · 健身 · 健康）
- Education & Learning（教育 · 知识分享）
- Finance & Investing（理财 · 投资 · 商业）
- Pets & Animals（宠物 · 动物）
- Music & Dance（音乐 · 舞蹈）
- Arts, Crafts & DIY（手工 · DIY · 艺术）
- Social Commentary & Current Affairs（社会议题 · 时事评论）
- Home Renovation & Real Estate（家居改造 · 房产）
- Automotive & Motorsports（汽车 · 机车）
- Parenting & Family Life（亲子 · 家庭生活）
- Mindfulness & Spiritual Growth（精神成长 · 身心灵）
- ASMR & Relaxation（ASMR · 放松治愈）
- Science & Experiments（科普 · 实验）
- Photography & Filmmaking（摄影 · 影像创作）
- Environmental & Sustainability（环保 · 可持续）
- Books & Literature（书籍 · 阅读文化）
- Hobbies & Collectibles（兴趣收藏 · 模型手办）""",
        max_new_tokens=128
    )
    
    # # Example 2: Process single image
    # image_path = "./image1.jpg"
    
    # print("\n=== Processing Image ===")
    # image_result = processor.img_to_text(
    #     image_path=image_path,
    #     prompt="Describe this image in detail.",
    #     max_new_tokens=1024
    # )
    
    # # Example 3: Process text with prefix
    # text_content = "人工智能的发展趋势和未来前景"
    
    # print("\n=== Processing Text ===")
    # text_result = processor.text_to_text_with_prefix(
    #     text=text_content,
    #     prefix="请分析以下内容并给出详细回答：",
    #     max_new_tokens=1024
    # )
    
    # # Save results
    # all_results = {
    #     "videos": video_results,
    #     "image": image_result,
    #     "text": text_result
    # }
    
    # processor.save_results(all_results, "batch_processing_results.json")
    
    # # Print summary
    # print(f"\n=== Summary ===")
    # print(f"Videos processed: {len(video_results)}")
    # print(f"Image processed: 1")
    # print(f"Text processed: 1")
    
    # successful_videos = sum(1 for r in video_results if r["success"])
    
    # print(f"Successful videos: {successful_videos}/{len(video_results)}")
    # print(f"Image processing successful: {image_result['success']}")
    # print(f"Text processing successful: {text_result['success']}") 