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

### **1. Nutzung als Python-Skript**
Falls du Python installiert hast, kannst du das Skript direkt ausführen:

```bash
python obs_asset_manager.py
```

### **2. Nutzung als EXE-Datei (Windows)**
Alternativ kannst du die vorkompilierte `.exe`-Datei verwenden, ohne Python zu installieren:
1. Lade die Datei `OBS_Asset_Manager.exe` herunter.
2. Doppelklicke die `.exe`, um das Programm zu starten.

Falls du das Programm selbst als `.exe` bauen möchtest, führe folgenden Befehl aus:

```bash
pyinstaller --onefile --windowed --name "OBS_Asset_Manager" obs_asset_manager.py
```

Die erstellte `.exe` findest du anschließend im `dist/`-Ordner.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der Datei [LICENSE](LICENSE).

## Download

Du kannst das Repository [hier herunterladen](https://github.com/dein-benutzername/obs-asset-manager) (ersetze den Link durch den tatsächlichen Repository-Link).

---

*Viel Erfolg mit deinem OBS Asset Manager!*
