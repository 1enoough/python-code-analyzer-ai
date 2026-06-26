import ast
import subprocess
import os
import tempfile
from radon.complexity import cc_visit

def analyze_code(code: str) -> dict:
    score = 100
    issues = []

    # 1. Sözdizimi (Syntax) Kontrolü
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {
            "score": 0,
            "issues": [f"Satır {e.lineno}: Sözdizimi hatası (SyntaxError) - {e.msg}"],
        }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        # 2. Flake8 Analizi
        # F401: module imported but unused
        # F841: local variable is assigned to but never used
        # E, W: PEP8 hataları ve uyarıları
        result = subprocess.run(
            ['flake8', temp_path],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    line_no = parts[1]
                    error_msg = parts[3].strip()
                    code_id = error_msg.split(' ')[0]
                    
                    # Türkçe çeviri ve Puan düşme
                    if code_id == 'F401':
                        issues.append(f"Satır {line_no}: Kullanılmayan kütüphane import edilmiş ({error_msg})")
                        score -= 5
                    elif code_id == 'F841':
                        issues.append(f"Satır {line_no}: Tanımlanmış ama kullanılmayan değişken var ({error_msg})")
                        score -= 5
                    else:
                        # Diğer PEP8 ihlalleri
                        issues.append(f"Satır {line_no}: PEP8 Stil İhlali - {error_msg}")
                        score -= 2

        # 3. Radon ile Döngü Karmaşıklığı (Cyclomatic Complexity) Analizi
        blocks = cc_visit(code)
        for block in blocks:
            # block.complexity
            if block.complexity > 5: # 5'in üzeri karmaşık kabul edelim
                issues.append(f"Satır {block.lineno}: '{block.name}' fonksiyonunun/sınıfının döngü karmaşıklığı çok yüksek (Değer: {block.complexity}). Kodu basitleştirin.")
                score -= 10

    finally:
        os.remove(temp_path)

    # Minimum puan 0 olmalı
    score = max(0, score)

    return {
        "score": score,
        "issues": issues
    }
