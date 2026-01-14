# requirements:

transformers>=4.57.0
qwen-vl-utils>=0.0.14
torch==2.8.0


# Basic Usage Example:
```py
from scripts.qwen3_vl_embedding import Qwen3VLEmbedder
import numpy as np
import torch

# Define a list of query texts
queries = [
    {"text": "A woman playing with her dog on a beach at sunset."},
    {"text": "Pet owner training dog outdoors near water."},
    {"text": "Woman surfing on waves during a sunny day."},
    {"text": "City skyline view from a high-rise building at night."}
]

# Define a list of document texts and images
documents = [
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."},
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
]

# Specify the model path
model_name_or_path = "Qwen/Qwen3-VL-Embedding-2B"

# Initialize the Qwen3VLEmbedder model
model = Qwen3VLEmbedder(model_name_or_path=model_name_or_path)
# We recommend enabling flash_attention_2 for better acceleration and memory saving,
# model = Qwen3VLEmbedder(model_name_or_path=model_name_or_path, torch_dtype=torch.float16, attn_implementation="flash_attention_2")

# Combine queries and documents into a single input list
inputs = queries + documents

# Process the inputs to get embeddings
embeddings = model.process(inputs)

# Compute similarity scores between query embeddings and document embeddings
similarity_scores = (embeddings[:4] @ embeddings[4:].T)

# Print out the similarity scores in a list format
print(similarity_scores.tolist())

# [[0.8157786130905151, 0.7178360223770142, 0.7173429131507874], [0.5195091962814331, 0.3302568793296814, 0.4391537308692932], [0.3884059488773346, 0.285782128572464, 0.33141762018203735], [0.1092604324221611, 0.03871120512485504, 0.06952016055583954]]
```

# vLLM Basic Usage Example
```py
import argparse
import numpy as np
import os
from typing import List, Dict, Any
from vllm import LLM, EngineArgs
from vllm.multimodal.utils import fetch_image


# Define a list of query texts
queries = [
    {"text": "A woman playing with her dog on a beach at sunset."},
    {"text": "Pet owner training dog outdoors near water."},
    {"text": "Woman surfing on waves during a sunny day."},
    {"text": "City skyline view from a high-rise building at night."}
]

# Define a list of document texts and images
documents = [
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."},
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
]

def format_input_to_conversation(input_dict: Dict[str, Any], instruction: str = "Represent the user's input.") -> List[Dict]:
    content = []
    
    text = input_dict.get('text')
    image = input_dict.get('image')
    
    if image:
        image_content = None
        if isinstance(image, str):
            if image.startswith(('http', 'https', 'oss')):
                image_content = image
            else:
                abs_image_path = os.path.abspath(image)
                image_content = 'file://' + abs_image_path
        else:
            image_content = image
        
        if image_content:
            content.append({
                'type': 'image', 
                'image': image_content,
            })
    
    if text:
        content.append({'type': 'text', 'text': text})
    
    if not content:
        content.append({'type': 'text', 'text': ""})
    
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content}
    ]
    
    return conversation

def prepare_vllm_inputs(input_dict: Dict[str, Any], llm, instruction: str = "Represent the user's input.") -> Dict[str, Any]:
    text = input_dict.get('text')
    image = input_dict.get('image')
    
    conversation = format_input_to_conversation(input_dict, instruction)
    
    prompt_text = llm.llm_engine.tokenizer.apply_chat_template(
        conversation, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    multi_modal_data = None
    if image:
        if isinstance(image, str):
            if image.startswith(('http', 'https', 'oss')):
                try:
                    image_obj = fetch_image(image)
                    multi_modal_data = {"image": image_obj}
                except Exception as e:
                    print(f"Warning: Failed to fetch image {image}: {e}")
            else:
                abs_image_path = os.path.abspath(image)
                if os.path.exists(abs_image_path):
                    from PIL import Image
                    image_obj = Image.open(abs_image_path)
                    multi_modal_data = {"image": image_obj}
                else:
                    print(f"Warning: Image file not found: {abs_image_path}")
        else:
            multi_modal_data = {"image": image}
    
    result = {
        "prompt": prompt_text,
        "multi_modal_data": multi_modal_data
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="Offline Similarity Check with vLLM")
    parser.add_argument("--model-path", type=str, default="models/Qwen3-VL-Embedding-2B", help="Path to the model")
    parser.add_argument("--dtype", type=str, default="bfloat16", help="Data type (e.g., bfloat16)")
    args = parser.parse_args()

    print(f"Loading model from {args.model_path}...")
    
    engine_args = EngineArgs(
        model=args.model_path,
        runner="pooling",
        dtype=args.dtype,
        trust_remote_code=True,
    )
    
    llm = LLM(**vars(engine_args))
    
    all_inputs = queries + documents
    vllm_inputs = [prepare_vllm_inputs(inp, llm) for inp in all_inputs]
    
    
    outputs = llm.embed(vllm_inputs)
    
    embeddings_list = []
    for i, output in enumerate(outputs):
        emb = output.outputs.embedding
        embeddings_list.append(emb)
        print(f"Input {i} embedding shape: {len(emb)}")
    
    embeddings = np.array(embeddings_list)
    print(f"\nEmbeddings shape: {embeddings.shape}")
    
    num_queries = len(queries)
    query_embeddings = embeddings[:num_queries]
    doc_embeddings = embeddings[num_queries:]
    
    similarity_scores = query_embeddings @ doc_embeddings.T
    
    print("\nSimilarity Scores:")
    print(similarity_scores.tolist())
    

if __name__ == "__main__":
    main()
```