import pytesseract

print("=== TEST TESSERACT ===")

try:
    version = pytesseract.get_tesseract_version()
    print("Version Tesseract :", version)
except Exception as e:
    print("ERREUR TESSERACT :", e)

try:
    langues = pytesseract.get_languages(config="")
    print("Langues disponibles :", langues)
except Exception as e:
    print("ERREUR LANGUES :", e)

print("=== FIN DU TEST ===")
