# Stef Peaks!

Dit script bestaat uit twee onderdelen. Een excel lezer (load_excel.py) en een csv lezer (load_csv.py). Excel is voor het schema en csv voor TP bestanden.

## Python installeren

Installeer eerst python (of anaconda) op je pc. Als het goed is moet je nu in een terminal de commando's `python` en `pip` kunnen draaien. Navigeer vervolgens naar de projectmap en voer dan de volgende code uit:
`$ pip install -r requirements.txt`
Hiermee installeer je alle libraries die nodig zijn.

## CSV Lezer

Om TP files te analyzeren moet je inloggen op TP en daar in de settings 'Workout Summaries' exporteren. Deze horen dan thuis in de 'workouts' map. Laat deze files als een .zip bestand staan, de loader maakt er automatisch csv documenten van.

Vervolgens is het een kwestie van het uitvoeren van het script: `python load_csv.py`. Het script vraagt om welke roeier je wil analyseren en produceert een plot in de 'plots' map.