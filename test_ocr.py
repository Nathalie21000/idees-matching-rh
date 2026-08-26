import pytesseract
from PIL import Image

print("Tesseract détecté :")
print(pytesseract.get_tesseract_version())

print("\nLangues disponibles :")
print(pytesseract.get_languages(config=""))

print("\nOCR prêt.")
