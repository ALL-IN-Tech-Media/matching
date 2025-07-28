from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch

# Load model and processor once (global, for efficiency)
MODEL_PATH = "./models/Qwen2.5-VL-32B-Instruct-AWQ"

def get_model_and_processor():
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(MODEL_PATH)
    return model, processor

model, processor = get_model_and_processor()

def video_to_text(video_url: str, prompt: str = "Describe this video.", max_new_tokens: int = 128) -> str:
    """
    Given a video URL or local path, return the generated text from the Qwen2.5-VL model.
    Args:
        video_url (str): Path or URL to the video file.
        prompt (str): The prompt/question to ask about the video.
        max_new_tokens (int): Maximum number of tokens to generate.
    Returns:
        str: The generated text output from the model.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": video_url,
                    # You can add more video kwargs here if needed
                    "max_pixels": 360 * 420,
                    "fps": 1.0,
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)
    # 保存变量内容到txt文件，处理Tensor类型
    def tensor_to_str(obj):
        if hasattr(obj, 'tolist'):  # Tensor对象
            return f"Tensor(shape={list(obj.shape)}, dtype={obj.dtype}, device={obj.device})"
        elif isinstance(obj, dict):
            return {k: tensor_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [tensor_to_str(item) for item in obj]
        else:
            return str(obj)
    
    # 保存image_inputs
    with open("image_inputs.txt", "w", encoding="utf-8") as f:
        f.write("Image Inputs:\n")
        f.write(str(tensor_to_str(image_inputs)))
    
    # 保存video_inputs
    with open("video_inputs.txt", "w", encoding="utf-8") as f:
        f.write("Video Inputs:\n")
        f.write(str(tensor_to_str(video_inputs)))
    
    # 保存video_kwargs
    with open("video_kwargs.txt", "w", encoding="utf-8") as f:
        f.write("Video Kwargs:\n")
        f.write(str(tensor_to_str(video_kwargs)))
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
        **video_kwargs,
    )

    inputs = inputs.to(model.device)
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    # 清理缓存，防止内存积累
    try:
        # 删除中间变量
        del inputs, generated_ids, generated_ids_trimmed, image_inputs, video_inputs, video_kwargs
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except Exception as e:
        print(f"GPU memory cleanup failed: {e}")
    
    return output_text[0] if output_text else ""

# Example usage (for testing)
if __name__ == "__main__":
    video_path = "./YING.MOV"
    prompt = """ROLE & GOAL:
You are an AI video analyst. Your goal is to watch a video (or read its description) and extract a specific set of attributes about the people and language in it.
INSTRUCTIONS:
From the video information I provide, identify the following attributes. Be concise and accurate.
Skin Tone: Describe the primary person's skin tone (e.g., Fair, Yellow, Brown, Dark, Light, Medium, Deep).
Gender: Identify the primary person's gender (Male, Female).
Ethnicity: Identify the primary person's ethnicity (White, Black, Latino, Asian).
Language: State the primary language spoken in the video.
Couple Appears?: Answer Yes or No.
Pet Appears?: Answer Yes or No.
Child Appears?: Answer Yes or No.
EXAMPLE:
Video Description: "A fair-skinned man and woman are speaking English in their living room, reviewing a new phone. Their dog, a golden retriever, walks past in the background."
Correct Output:
Skin Tone: Fair
Gender: Male & Female
Ethnicity: White
Language: English
Couple Appears?: Yes
Pet Appears?: Yes
Child Appears?: No
YOUR TASK:
Now, analyze the following video and provide the output in the same format.
[PASTE VIDEO DESCRIPTION OR TRANSCRIPT HERE]"""
    result = video_to_text(video_path, prompt=prompt, max_new_tokens=2048)
    
    print(result) 