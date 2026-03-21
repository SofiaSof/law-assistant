# Ustanovka Tesseract OCR

## Sposob 1: Ustanovka s sayta (rekomenduyu)

1. Pereydite na: https://github.com/UB-Mannheim/tesseract/wiki
2. Skachayte ustanovshchik dlya Windows
3. Ustanovite programmu
4. Dobavte put `C:\Program Files\Tesseract-OCR\` v sistemnyy PATH
5. Pri ustanovke vybierte russkiy yazykovoy paket

## Sposob 2: Chocolatey

```bash
choco install tesseract
```

## Sposob 3: Winget

```bash
winget install --id Google.TesseractOCR --accept-source-agreements
```

## Posle ustanovki

Pereзапустиte terminal i proverьte:

```bash
tesseract --version
```

## Esli Tesseract ne ustanovlen

Programma budet rabotat v demo-rezhime - vыdaleet soobschenie s instruktsiyami po ustanovke, no ne smozhet raspoznavat tekst s izobrazheniy.

## Proverka v programme

Posle ustanovki Tesseract:

```bash
python law_assistant.py /image put/k/izobrazheniy.png
```
