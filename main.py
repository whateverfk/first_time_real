import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_APi_router():

    api =os.getenv("OPENROUTER_API_KEY")

    if not api:
        print("bro where the key")
        raise ValueError(
            "no thit wtf"
            " he he he"
        )
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api
    )
    return client

def test_connect(model,prompt):
    try:
        client= test_APi_router()

        completion = client.chat.completions.create(

            model=model,
            messages=[
                 {"role": "system", "content": "You are a helpful assistant."},
                 {"role":"user","content":prompt}

            ]
        )   
        
        return completion.choices[0].message.content

    except Exception as e:
        print( f" something wrong fr {e} ")

def compare_model(prompt):
    models = {
        "DeepSeek: R1 0528 (free)": "deepseek/deepseek-r1-0528:free",
        "DeepSeek: Deepseek R1 0528 Qwen3 8B (free)": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "Sarvam AI: Sarvam-M (free)": "sarvamai/sarvam-m:free",
        "Google: Gemma 3n 4B (free)": "google/gemma-3n-e4b-it:free"
    }

    print(f"Prompt: {prompt}\n")
    print("-" * 50)

    for name, model_id in models.items():
        try:
            print(f"\n{name} ({model_id}):")
            response = test_connect(model_id, prompt)
            print(f"Response: {response}\n")
            print("-" * 50)
        except Exception as e:
            print(f"Error with {name}: {str(e)}")
            print("-" * 50)

if __name__ == "__main__":
    text = input("NHap gi do di:")
    prompt=f"hãy sửa lỗi ngữ pháp và chính tả của đoạn sau : {text} và giữ cho độ dài tối đa là độ dài của đoạn text*2 + 50 "
    compare_model(prompt)
        