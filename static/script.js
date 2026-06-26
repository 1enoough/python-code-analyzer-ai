document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('code-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');
    const scoreDisplay = document.getElementById('score-display');
    const scoreValue = document.getElementById('score-value');
    const issuesCard = document.getElementById('issues-card');
    const issuesList = document.getElementById('issues-list');
    const aiCard = document.getElementById('ai-card');
    const aiSuggestionContent = document.getElementById('ai-suggestion-content');

    const setLoading = (isLoading) => {
        if (isLoading) {
            analyzeBtn.disabled = true;
            btnText.textContent = "Analiz Ediliyor...";
            spinner.classList.remove('hidden');
            resultContainer.classList.add('hidden');
        } else {
            analyzeBtn.disabled = false;
            btnText.textContent = "Kodu Analiz Et";
            spinner.classList.add('hidden');
        }
    };

    const updateScoreRing = (score) => {
        scoreDisplay.className = 'score-circle'; // reset
        if (score >= 80) {
            scoreDisplay.classList.add('score-great');
        } else if (score >= 50) {
            scoreDisplay.classList.add('score-good');
        } else {
            scoreDisplay.classList.add('score-bad');
        }

        // Animate counter
        let start = 0;
        const duration = 1500;
        let startTime = null;
        
        const step = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            // easeOutQuart
            const easeProgress = 1 - Math.pow(1 - progress, 4);
            const currentObj = Math.floor(easeProgress * score);
            
            scoreValue.textContent = currentObj;
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                scoreValue.textContent = score;
            }
        };
        window.requestAnimationFrame(step);
    };

    analyzeBtn.addEventListener('click', async () => {
        const code = codeInput.value.trim();
        if (!code) {
            alert('Lütfen analiz edilecek bir Python kodu girin.');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Bir hata oluştu");
            }

            const data = await response.json();
            
            // Puanı Ayarla
            updateScoreRing(data.score);

            // Hataları Listele
            issuesList.innerHTML = '';
            if (data.issues && data.issues.length > 0) {
                issuesCard.classList.remove('hidden');
                data.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.textContent = issue;
                    issuesList.appendChild(li);
                });
            } else {
                issuesCard.classList.add('hidden');
            }

            // Yapay Zeka Önerisi
            if (data.ai_suggestion) {
                aiCard.classList.remove('hidden');
                // parse markdown
                aiSuggestionContent.innerHTML = marked.parse(data.ai_suggestion);
                // highlight code blocks inside AI response
                Prism.highlightAllUnder(aiSuggestionContent);
            } else {
                aiCard.classList.add('hidden');
            }

            resultContainer.classList.remove('hidden');

            // Scroll to results
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            alert('Hata: ' + error.message);
        } finally {
            setLoading(false);
        }
    });

    // Handle tab indent passing
    codeInput.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;

            // insert 4 spaces
            this.value = this.value.substring(0, start) +
                "    " + this.value.substring(end);

            this.selectionStart =
                this.selectionEnd = start + 4;
        }
    });
});
