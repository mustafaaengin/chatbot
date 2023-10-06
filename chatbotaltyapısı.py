from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import openai

# similarity hesaplaması
def calculate_cosine_similarity(text1, text2):
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1]

# gitden veri çekme
url = "raw address of your github file"
response = requests.get(url)
lines = response.text.strip().split("\n")

while True:
    # kullanıcı metnini al
    user_question = input("Lütfen sorunuzu girin (çıkmak için 'exit' yazın): ")
    
    if user_question.lower() == 'exit':
        break

    similar_texts = []

    # her satırdaki prompt ve completion ile benzerlik hesapla
    for line in lines:
        data = eval(line)
        prompt_similarity = calculate_cosine_similarity(user_question, data.get("prompt", ""))
        completion_similarity = calculate_cosine_similarity(user_question, data.get("completion", ""))
        
        # prompt %40tan büyük benzerlikteyse hem promptı hem de completionı sakla
        if prompt_similarity > 0.4:
            similar_texts.append(data.get("prompt", ""))
            similar_texts.append(data.get("completion", ""))
        # completion %40tan büyük benzerlikteyse hem promptı hem de completionı sakla
        elif completion_similarity > 0.4:
            similar_texts.append(data.get("prompt", ""))
            similar_texts.append(data.get("completion", ""))

    # benzerlik oranı %40'ın altındaysa openaia yönlendir
    if not similar_texts:
        openai.api_key = "apikey1"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_question}]
        )
        answer = response.choices[0].message['content'].strip()
        print(f"ChatGPT 3.5 Turbo'dan cevap: {answer}")
    else:
        combined_texts = "\n".join(similar_texts)
        prompt_for_gpt = f"Soru: {user_question}\nVerilen Bilgiler: {combined_texts}\nBu bilgileri kullanarak cevap verin: "
       
        openai.api_key = "apikey2"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_for_gpt}]
        )
        answer = response.choices[0].message['content'].strip()
        print(f"ChatGPT 3.5 Turbo'dan cevap (GitHub verileri kullanılarak): {answer}")
