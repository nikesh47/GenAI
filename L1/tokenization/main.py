import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello, This is Nikesh here"
tokens = enc.encode(text)


print("Tokens:", tokens)

Tokens= [13225, 11, 1328, 382, 29721, 8382, 2105]

decoded = enc.decode(tokens)

print("Decoded:", decoded)
