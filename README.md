# OBS Asset Manager

Dieses Python-Skript bietet eine grafische Benutzeroberfläche (GUI) zur Verarbeitung von OBS-Exporten im JSON-Format.  
Es ermöglicht dir, Assets (z. B. Bilder, Videos) aus einem OBS-Export in einen von dir definierten Zielordner zu kopieren –  
und zwar **pro Scene**. Zusätzlich kann das Skript die Dateipfade in der JSON aktualisieren,  
oder ein reines Backup der Assets erstellen.

## Features

- **Assets kopieren & Pfade anpassen:**  
  Erstelle für jede Scene einen Ordner und kopiere alle darin referenzierten Assets in diesen Ordner.  
  Bei erfolgreichem Kopiervorgang wird der Dateipfad in der JSON auf den neuen (absoluten) Pfad aktualisiert.
  
- **Nur Pfad aktualisieren:**  
  Aktualisiere in der JSON alle Dateipfade, indem du einen alten Basis-Pfad durch einen neuen ersetzt.
  
- **Nur Assets backupen:**  
  Kopiere alle referenzierten Assets in einen separaten Backup-Ordner, ohne die JSON zu verändern.

- **Fehlerprotokoll:**  
  Falls das Kopieren einzelner Assets fehlschlägt (z. B. wenn eine Datei nicht vorhanden ist),  
  wird in dem entsprechenden Scene-Ordner eine Textdatei `missing_files.txt` erstellt,  
  in der alle fehlenden Dateipfade aufgeführt sind.

- **Exportordner öffnen:**  
  Nach Abschluss der Verarbeitung wird der entsprechende Zielordner automatisch im Dateiexplorer geöffnet.

## Voraussetzungen

- Python 3.6 oder höher  
- Standardmodule: `os`, `json`, `shutil`, `tkinter`, `subprocess`, `platform`

Das Skript verwendet ausschließlich Standard-Python-Bibliotheken, sodass keine zusätzlichen Pakete installiert werden müssen.

## Nutzung

1. **Skript starten:**  
   Führe das Skript über die Kommandozeile oder per Doppelklick aus:

   ```bash
   python obs_asset_manager.py
   ```

2. **OBS Export JSON auswählen:**  
   Klicke auf den Button "Auswählen" neben dem Eingabefeld, um deine OBS Export JSON-Datei auszuwählen.

3. **Modus wählen:**  
   Wähle einen der drei Modi über die Radiobuttons:
   - *Assets kopieren & Pfade anpassen:*  
     Kopiert alle Assets in einen Zielordner und passt die JSON-Pfade an.
   - *Nur Pfad aktualisieren:*  
     Aktualisiert ausschließlich die Dateipfade in der JSON.
   - *Nur Assets backupen:*  
     Erstellt ein Backup aller Assets in einem separaten Ordner, ohne die JSON zu verändern.

4. **Zielordner auswählen:**  
   Wähle den entsprechenden Zielordner (für Kopieren, Backup oder den Ordner, in dem die aktualisierte JSON gespeichert werden soll).

5. **Starten:**  
   Klicke auf "Start", um den Prozess zu starten.  
   Bei Fehlermeldungen (z. B. wenn bestimmte Dateien nicht gefunden werden) werden diese in einer Textdatei `missing_files.txt` im entsprechenden Scene-Ordner protokolliert und in einer Erfolgsmeldung angezeigt.

6. **Exportordner öffnen:**  
   Nach Abschluss des Vorgangs wird der entsprechende Zielordner automatisch im Dateiexplorer geöffnet.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der Datei [LICENSE](LICENSE).

## Download

Du kannst das Repository [hier herunterladen](https://github.com/dein-benutzername/obs-asset-manager) (ersetze den Link durch den tatsächlichen Repository-Link).

---

*Viel Erfolg mit deinem OBS Asset Manager!*
