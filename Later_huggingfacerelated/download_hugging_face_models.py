# # download_model.py
# from transformers import AutoModel, AutoTokenizer
# import os

# os.environ['HF_HOME'] = "D:/AI_Models/huggingface"

# model_name = "deepseek-ai/DeepSeek-OCR"
# cache = "D:/AI_Models/huggingface"

# print("Downloading...")
# AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, cache_dir=cache)
# AutoModel.from_pretrained(model_name, trust_remote_code=True, cache_dir=cache)
# print("Done!")

# from transformers import AutoModel, AutoTokenizer
# import torch
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = '0'
# model_name = 'deepseek-ai/DeepSeek-OCR'
# cache = "D:/AI_Models/huggingface"
# tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True,cache_dir=cache)
# model = AutoModel.from_pretrained(model_name, _attn_implementation='flash_attention_2', trust_remote_code=True, use_safetensors=True)
# model = model.eval().cuda().to(torch.bfloat16)
# print("Done!")