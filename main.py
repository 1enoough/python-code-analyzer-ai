from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from analyzer import analyze_code
from ai_helper import get_improvement_suggestion

app = FastAPI(title="Python Kod Analizörü ve Yapay Zeka Asistanı")

# Statik dosyaları sunmak için (index.html, style.css, script.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

class CodeRequest(BaseModel):
    code: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def analyze_code_endpoint(request: CodeRequest):
    code = request.code
    if not code.strip():
        raise HTTPException(status_code=400, detail="Kod alanı boş olamaz.")
    
    # Kodu analiz et
    analysis_result = analyze_code(code)
    
    # Yapay zekadan öneri al
    # Eğer çok fazla hata varsa veya karmaşıklık yüksekse
    ai_suggestion = await get_improvement_suggestion(code, analysis_result)
    
    return {
        "score": analysis_result["score"],
        "issues": analysis_result["issues"],
        "ai_suggestion": ai_suggestion
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

