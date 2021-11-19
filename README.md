# COVID-19 Italy Tracker

## Cosa è

Poco prima dell'inizio del lockdown che ha interessato l'intero stato italiano tra i mesi di marzo e maggio 2020, la protezione civile ha iniziato la pubblicazione dei dati giornalieri sull'andamento epidemiologico in Italia in questo repository pubblico: [GitHub - pcm-dpc/COVID-19: COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19). I dati contenuti in questo repository sono gli stessi dati utilizzati dal governo per monitorare l'andamento epidemiologico e decidere eventuali nuove misure restrittive (o allentare le preesistenti). Questi stessi dati sono inoltre quelli comunicati dai vari mass media, nonché quelli comunicati dallo stesso Ministero della Salute nel canale Telegram ufficiale. Il problema è che tutti parlano degli incrementi giornalieri, rapportando raramente tale valore al numero di tamponi giornalieri effettuati, e non dando così un quadro più chiaro e immediato circa l'andamento epidemiologico in termini di crescite e decrescite. COVID-19 Italy Tracker è nato proprio per sopperire a questa mancanza.

## Come funziona

COVID-19 Italy Tracker utilizza gli stessi dati ufficiali del repository pubblico della protezione civile ([GitHub - pcm-dpc/COVID-19: COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19)), perciò non si occupa di scaricare autonomamente i dati dalla rete, ma è compito dell'utente scaricare periodicamente i nuovi dati sui quali il programma lavora. Una volta fatto questo è sufficiente passare al programma il percorso della cartella radice contenente i dati e il programma provvederà ad analizzare, sia nazionalmente che per singole regioni, i dati dall'inizio dell'epidemia ai più recenti disponibili nel repository. Giorno per giorno il programma calcola, in base al numero di nuovi casi giornalieri e al numero di tamponi effettuati, un valore in percentuale di crescita o di decrescita. Infine, stima i valori futuri di crescita (o di decrescita) tramite regressione lineare, e mostra il risultato in un grafico.

## Requisiti

Il programma è stato interamente scritto in Python 3, appoggiandosi alle librerie seaborn, numpy, pandas e scikit-learn. E' consigliato l'utilizzo di Anaconda (o miniconda).

## NOTA

Questo programma viene reso disponibile al solo scopo di analizzare i dati forniti dalla protezione civile. Non è stato pensato come sostituzione alle comunicazioni ufficiali del governo e del Ministero della Salute, che devono continuare ad essere considerate dagli utenti come le uniche fonti ufficiali di informazioni circa l'andamento epidemiologico.
