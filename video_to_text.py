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

def video_to_text(video_url: str, prompt: str = "Describe this video.") -> str:
    """
    Given a video URL or local path, return the generated text from the Qwen2.5-VL model.
    Args:
        video_url (str): Path or URL to the video file.
        prompt (str): The prompt/question to ask about the video.
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
        generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return output_text[0] if output_text else ""

# Example usage (for testing)
if __name__ == "__main__":
    video_path = "../videos/tiktok_@.aplacetoheal_0.mp4"
    result = video_to_text(video_path)
    print(result) 