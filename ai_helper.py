import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def get_improvement_suggestion(code: str, analysis_result: dict) -> str:
    """
    Kodu parçalar ve Gemini ile analiz ederek Türkçe iyileştirme önerisi döner.
    """
    if not GEMINI_API_KEY:
        return "Gemini API anahtarı bulunamadı. Lütfen .env dosyasını kontrol edin."

    if analysis_result["score"] == 100:
        return "Kodunuz harika görünüyor! Temiz kod prensiplerine uygun."

    # Prompt hazırlama
    issues_text = "\n".join(analysis_result["issues"])
    prompt = f"""
    Aşağıda verilen Python kodunun analiz sonuçlarına göre birtakım stilistik ve yapısal hataları var:
    
    Hatalar:
    {issues_text}
    
    Kod:
    ```python
    {code}
    ```
    
    Lütfen bu kodu temiz kod (clean code) prensiplerine uygun olarak yeniden yaz ve yaptığın değişiklikleri kısaca, anlaşılır bir şekilde Türkçe olarak açıkla. Yalnızca Türkçe yanıt ver ve Markdown formatında kod bloklarını kullan.
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        # Alternatif olarak 'gemini-1.5-flash' da kullanılabilir, model erişimine göre.
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Yapay zeka önerisi alınırken bir hata oluştu: {str(e)}"
