from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("qwen05-finetuned-lora8")

text = "Hello world! How are you?"
tokens = tok.tokenize(text) # ['Hello', 'world', '!', 'How', 'are', 'you', '?']
ids = tok.encode(text, add_special_tokens=True) # [101, 8667, 1362, 117, 1139, 1128, 136, 102] is the token ids with special tokens
back = tok.decode(ids)

print("tokens:", tokens)
print("ids:", ids)
print("decoded:", back)