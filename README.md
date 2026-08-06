# AI Desktop Search Assistant

## Run

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Selenium Manager downloads matching browser drivers automatically. Configure `OPENAI_API_KEY` in `.env` for AI query improvement and image analysis. OCR requires a local Tesseract installation on PATH.

## Package

```powershell
pyinstaller --noconsole --name SearchAssistant --add-data ".env;." app.py
```
