# Masterarbeit

## Thema
Im Rahmen dieser Mastermasterabeit wurde ein Clinical Decision Support System (CDSS) für die Diagnostik von Demenz entwickelt.


## Anwendung
Die webbasierte Anwendung basiert auf Docker. Für die Vorraussetzungen und Installation von Docker wird auf die [Docker-Dokumentatation](https://docs.docker.com/) verwießen.
 Um sie verwenden zu konnen muss zu erst das Images gebaut werden. Dies geht mit folgendem Befehl, der nach eigenen Anforderungen angepasst werden kann:

```shell
docker build -t demenz-cdss .
```

CAVE: die Images Erstellung kann je nach verfügbarer Internetgeschwindigkeit mehrere Minuten dauern.


Der Docker-Container kann mit folgendem Befehl gestartet werden. Die Anwendung ist sollte anschließend unter http://localhost:5000 erreichbar sein.

```shell
docker run -p 5000:5000 demenz-cdss
```

## Devcontainer
Die Anwendung als auch die Datenverarbeitung und Modellbildung wurden mittels Devcontainer entwickelt. Die Devcontainer-Konfigurationsdatei wurde für VS-Code entwickelt. Sie sollte jedoch auch für andere IDEs mit Devcontainer-Support anstandslos funktionieren. Für die Vorraussetzung von Verwendung Devcontainer unter VS-Code, wird auf deren [Dokumentation](https://code.visualstudio.com/docs/devcontainers/containers) verwiesen.

Wurden alle nötigen Vorrausetzungen erfüllt kann mit `STRG+SHIFT+P` kann in VS-Code die Befehlspalette geöffnet werden. Dort muss `Dev Containers: Reopen in Container` gewählt werden. Anschließend kann zwischen

`Data Processing Container`
und
`Web-App Container`

gewählt werden. Die Images-Erstellung kann je nach verfügbarer Internetgeschwindigkeit mehrere Minuten dauern. Der `Web-App Container` startet automatisch eine Flask-Server. Im Bedarffall kann dieser auch manuell mittels

```shell
flask --app src/app run --host=0.0.0.0 --port=5001 --debug
```

gestartet werden. Die Anwendung sollte unter http://localhost:5001 erreichbar sein

Die Source-Code für die Datenverarbeitung und Modellbildung befindet sich unter `src/data-processing`. Die Datenordern, Konfigurationsdateien und erstellten Modelle finden sich unter `data`.