import google.generativeai as genai

# Put your actual API key here
genai.configure(api_key="AIzaSyClVW5_jB5ece4rNYMsIjHbETbGO78YQMk")

print("Models available to your API key:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)