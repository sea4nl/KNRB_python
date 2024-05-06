# Stef Peaks!

Dit script bestaat uit twee onderdelen. Een excel lezer (load_excel.py) en een csv lezer (load_csv.py). Excel is voor het schema en csv voor TP bestanden.

## CSV Lezer

Om TP files te analyzeren moet je inloggen op TP en daar in de settings 'Workout Summaries' exporteren. Deze horen dan thuis in de 'workouts' map. Laat deze files als een .zip bestand staan, de loader maakt er automatisch csv documenten van.

Vervolgens is het een kwestie van het uitvoeren van het script: `python load_csv.py`. Het script vraagt om welke roeier je wil analyseren en produceert een plot in de 'plots' map.