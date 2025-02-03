#!/usr/bin/env python3
import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform

def sanitize_filename(name):
    """Ersetzt Zeichen, die in Dateinamen unzulässig sind."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

def process_file(file_path, target_folder):
    """
    Versucht, file_path in target_folder zu kopieren.
    Liefert den absoluten Pfad der kopierten Datei zurück oder None, falls ein Fehler auftritt.
    """
    if not os.path.isfile(file_path):
        print(f"Warnung: Datei '{file_path}' nicht gefunden. Überspringe.")
        return None
    os.makedirs(target_folder, exist_ok=True)
    filename = os.path.basename(file_path)
    new_path = os.path.join(target_folder, filename)
    try:
        shutil.copy2(file_path, new_path)
        print(f"Kopiert: {file_path} -> {new_path}")
        return os.path.abspath(new_path)
    except Exception as e:
        print(f"Fehler beim Kopieren von {file_path}: {e}")
        return None

def copy_assets(json_data, dest_base, update_json=True):
    """
    Kopiert alle referenzierten Assets in den Zielordner dest_base –  
    es wird **pro Szene** ein Ordner erstellt.
    
    Es werden in den Scene-Objekten (entweder als Source-Objekte mit "id" == "scene"
    im "sources"-Array oder in einem separaten "scenes"/"Scenes"-Array)
    alle Dateipfade gesucht, die entweder direkt in den Einstellungen stehen
    oder in den Items als "private_settings" bzw. über den Verweis "source_uuid".
    
    Falls update_json True ist, werden in der JSON die Dateipfade auf den neuen absoluten Pfad aktualisiert.
    
    Rückgabe: (aktualisierte json_data, missing_files)
    """
    global_missing_files = []

    # Falls vorhanden, erstellen wir ein Mapping: uuid -> source (aus "sources")
    sources_dict = {}
    if "sources" in json_data:
        for source in json_data["sources"]:
            uuid = source.get("uuid")
            if uuid:
                sources_dict[uuid] = source

    def process_scene(scene, scene_folder):
        scene_missing_files = []  # Fehlende Dateien nur für diese Scene
        os.makedirs(scene_folder, exist_ok=True)
        # Zuerst: Prüfe direkt in den Einstellungen der Szene
        settings = scene.get("settings", {})
        for key in ["file", "local_file"]:
            if key in settings and isinstance(settings[key], str) and settings[key]:
                new_path = process_file(settings[key], scene_folder)
                if new_path:
                    if update_json:
                        settings[key] = new_path
                else:
                    scene_missing_files.append(settings[key])
                    global_missing_files.append(settings[key])
        # Jetzt: Gehe über alle Items der Szene
        items = settings.get("items", [])
        for item in items:
            file_path = None
            # Option 1: Direkt in private_settings
            priv = item.get("private_settings", {})
            if isinstance(priv, dict) and "file" in priv and isinstance(priv["file"], str) and priv["file"]:
                file_path = priv["file"]
            # Option 2: Falls kein direkter Pfad in private_settings vorhanden ist, 
            # versuche den Verweis via "source_uuid"
            elif "source_uuid" in item:
                src_uuid = item["source_uuid"]
                src = sources_dict.get(src_uuid)
                if src:
                    src_settings = src.get("settings", {})
                    for key in ["file", "local_file"]:
                        if key in src_settings and isinstance(src_settings[key], str) and src_settings[key]:
                            file_path = src_settings[key]
                            break
            # Falls ein Dateipfad gefunden wurde, kopieren wir die Datei
            if file_path:
                new_path = process_file(file_path, scene_folder)
                if new_path:
                    if update_json:
                        if "file" in priv:
                            item["private_settings"]["file"] = new_path
                        else:
                            item["copied_file"] = new_path
                else:
                    scene_missing_files.append(file_path)
                    global_missing_files.append(file_path)
        # Falls es fehlende Dateien in dieser Scene gab, erstelle eine Textdatei im Scene-Ordner
        if scene_missing_files:
            missing_file_path = os.path.join(scene_folder, "missing_files.txt")
            try:
                with open(missing_file_path, "w", encoding="utf-8") as mf:
                    mf.write("Folgende Dateien konnten nicht kopiert werden:\n")
                    mf.write("\n".join(scene_missing_files))
                print(f"Missing files list für Scene '{scene.get('name', 'Unbenannte_Szene')}' erstellt: {missing_file_path}")
            except Exception as e:
                print(f"Fehler beim Erstellen der Missing-Files-Datei in {scene_folder}: {e}")

    # Nun verarbeiten wir die Szenen. Wir unterscheiden zwei Fälle:
    # 1. Szenen sind in "sources" als Objekte mit "id" == "scene"
    # 2. Alternativ gibt es ein separates Array "scenes" oder "Scenes"
    if "sources" in json_data:
        for source in json_data["sources"]:
            if source.get("id") == "scene":
                scene_name = source.get("name", "Unbenannte_Szene")
                scene_folder = os.path.join(dest_base, sanitize_filename(scene_name))
                process_scene(source, scene_folder)
    else:
        scenes = json_data.get("scenes") or json_data.get("Scenes")
        if not scenes:
            messagebox.showerror("Fehler", "Keine Szenen in der JSON gefunden.\nÜberprüfe bitte den Schlüssel in deiner Datei.")
            return json_data, global_missing_files
        for scene in scenes:
            scene_name = scene.get("name", "Unbenannte_Szene")
            scene_folder = os.path.join(dest_base, sanitize_filename(scene_name))
            process_scene(scene, scene_folder)
            
    return json_data, global_missing_files

def update_paths(json_data, old_base, new_base):
    """
    Ersetzt in allen in der JSON auftretenden Dateipfaden (Schlüssel "file" oder "local_file")
    den alten Basis-Pfad durch den neuen. Die Funktion geht rekursiv alle Dicts und Listen durch.
    """
    def recursive_update(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ("file", "local_file") and isinstance(value, str):
                    if value.startswith(old_base):
                        new_value = new_base + value[len(old_base):]
                        print(f"Update: {value} -> {new_value}")
                        obj[key] = new_value
                else:
                    recursive_update(value)
        elif isinstance(obj, list):
            for item in obj:
                recursive_update(item)
    recursive_update(json_data)
    return json_data

def backup_assets(json_data, dest_base):
    """
    Kopiert alle referenzierten Assets (wie in copy_assets) in den Backup-Ordner dest_base,
    ohne die JSON zu verändern.
    
    Rückgabe: missing_files (Liste der Dateien, die nicht gefunden wurden)
    """
    _, missing_files = copy_assets(json_data, dest_base, update_json=False)
    return missing_files

def open_folder(folder):
    """
    Öffnet den angegebenen Ordner im Dateiexplorer, plattformabhängig.
    """
    try:
        if os.name == "nt":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception as e:
        print("Fehler beim Öffnen des Ordners:", e)

class OBSAssetManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OBS Asset Manager")
        self.geometry("650x550")
        self.resizable(False, False)

        # Variablen
        self.input_json_path = tk.StringVar()
        self.output_json_path = tk.StringVar()
        # Modi: "copy" (Assets kopieren & JSON anpassen), "update" (nur Pfad aktualisieren), "backup" (nur Assets backupen)
        self.mode = tk.StringVar(value="copy")
        self.dest_folder = tk.StringVar()
        self.old_base = tk.StringVar()
        self.new_base = tk.StringVar()
        self.backup_folder = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)

        # Eingabe JSON-Datei auswählen
        ttk.Label(frame, text="OBS Export JSON:").grid(row=0, column=0, sticky="w")
        entry_input = ttk.Entry(frame, textvariable=self.input_json_path, width=60)
        entry_input.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Auswählen", command=self.select_input_json).grid(row=0, column=2, padx=5)

        # Ausgabe JSON (optional)
        ttk.Label(frame, text="Ausgabe JSON (optional):").grid(row=1, column=0, sticky="w")
        entry_output = ttk.Entry(frame, textvariable=self.output_json_path, width=60)
        entry_output.grid(row=1, column=1, padx=5)
        ttk.Button(frame, text="Auswählen", command=self.select_output_json).grid(row=1, column=2, padx=5)

        # Modus-Auswahl
        ttk.Label(frame, text="Modus:").grid(row=2, column=0, sticky="w")
        mode_frame = ttk.Frame(frame)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(mode_frame, text="Assets kopieren & Pfade anpassen", variable=self.mode, value="copy", command=self.toggle_mode).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Nur Pfad aktualisieren", variable=self.mode, value="update", command=self.toggle_mode).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Nur Assets backupen", variable=self.mode, value="backup", command=self.toggle_mode).pack(side="left", padx=5)

        # Bereich für Copy-Modus: Zielordner auswählen
        self.copy_frame = ttk.LabelFrame(frame, text="Asset-Kopiermodus", padding="10")
        self.copy_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        ttk.Label(self.copy_frame, text="Zielordner:").grid(row=0, column=0, sticky="w")
        entry_dest = ttk.Entry(self.copy_frame, textvariable=self.dest_folder, width=50)
        entry_dest.grid(row=0, column=1, padx=5)
        ttk.Button(self.copy_frame, text="Ordner auswählen", command=self.select_dest_folder).grid(row=0, column=2, padx=5)

        # Bereich für Update-Only-Modus: Alte und neue Basis-Pfade
        self.update_frame = ttk.LabelFrame(frame, text="Update-Only-Modus", padding="10")
        self.update_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        ttk.Label(self.update_frame, text="Alter Basis-Pfad:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.update_frame, textvariable=self.old_base, width=50).grid(row=0, column=1, padx=5)
        ttk.Label(self.update_frame, text="Neuer Basis-Pfad:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.update_frame, textvariable=self.new_base, width=50).grid(row=1, column=1, padx=5)

        # Bereich für Backup-Modus: Backup-Zielordner auswählen
        self.backup_frame = ttk.LabelFrame(frame, text="Backup-Modus (nur Assets backupen)", padding="10")
        self.backup_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)
        ttk.Label(self.backup_frame, text="Backup Zielordner:").grid(row=0, column=0, sticky="w")
        entry_backup = ttk.Entry(self.backup_frame, textvariable=self.backup_folder, width=50)
        entry_backup.grid(row=0, column=1, padx=5)
        ttk.Button(self.backup_frame, text="Ordner auswählen", command=self.select_backup_folder).grid(row=0, column=2, padx=5)

        # Standardmäßig wird der Copy-Modus angezeigt
        self.toggle_mode()

        # Start-Button
        ttk.Button(frame, text="Start", command=self.start_process).grid(row=6, column=0, columnspan=3, pady=20)

    def select_input_json(self):
        filename = filedialog.askopenfilename(title="OBS Export JSON auswählen", filetypes=[("JSON Dateien", "*.json")])
        if filename:
            self.input_json_path.set(filename)

    def select_output_json(self):
        filename = filedialog.asksaveasfilename(title="Ausgabe JSON speichern", defaultextension=".json", filetypes=[("JSON Dateien", "*.json")])
        if filename:
            self.output_json_path.set(filename)

    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="Zielordner auswählen")
        if folder:
            self.dest_folder.set(folder)

    def select_backup_folder(self):
        folder = filedialog.askdirectory(title="Backup Zielordner auswählen")
        if folder:
            self.backup_folder.set(folder)

    def toggle_mode(self):
        """Blendet die entsprechenden Bereiche ein oder aus."""
        mode = self.mode.get()
        if mode == "copy":
            self.copy_frame.grid()
            self.update_frame.grid_remove()
            self.backup_frame.grid_remove()
        elif mode == "update":
            self.update_frame.grid()
            self.copy_frame.grid_remove()
            self.backup_frame.grid_remove()
        elif mode == "backup":
            self.backup_frame.grid()
            self.copy_frame.grid_remove()
            self.update_frame.grid_remove()

    def start_process(self):
        input_path = self.input_json_path.get()
        if not input_path or not os.path.isfile(input_path):
            messagebox.showerror("Fehler", "Bitte eine gültige OBS Export JSON-Datei auswählen.")
            return

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der JSON-Datei:\n{e}")
            return

        mode = self.mode.get()
        missing_files = []
        export_folder = None  # Zum späteren Öffnen
        if mode == "copy":
            dest = self.dest_folder.get()
            if not dest or not os.path.isdir(dest):
                messagebox.showerror("Fehler", "Bitte einen gültigen Zielordner auswählen.")
                return
            json_data, missing_files = copy_assets(json_data, os.path.abspath(dest), update_json=True)
            export_folder = os.path.abspath(dest)
        elif mode == "update":
            old_base = self.old_base.get()
            new_base = self.new_base.get()
            if not old_base or not new_base:
                messagebox.showerror("Fehler", "Bitte sowohl den alten als auch den neuen Basis-Pfad angeben.")
                return
            json_data = update_paths(json_data, os.path.abspath(old_base), os.path.abspath(new_base))
            missing_files = []  # Es werden keine Dateien kopiert
            export_folder = os.path.dirname(os.path.abspath(self.output_json_path.get() or input_path))
        elif mode == "backup":
            backup_dest = self.backup_folder.get()
            if not backup_dest or not os.path.isdir(backup_dest):
                messagebox.showerror("Fehler", "Bitte einen gültigen Backup Zielordner auswählen.")
                return
            missing_files = backup_assets(json_data, os.path.abspath(backup_dest))
            export_folder = os.path.abspath(backup_dest)

        output_path = self.output_json_path.get() if self.output_json_path.get() else input_path
        if mode in ("copy", "update"):
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern der JSON-Datei:\n{e}")
                return

        if mode == "backup":
            msg = f"Assets-Backup abgeschlossen in:\n{export_folder}"
        else:
            msg = f"JSON erfolgreich gespeichert unter:\n{output_path}"
        if missing_files:
            msg += "\n\nFolgende Dateien wurden nicht gefunden bzw. kopiert:\n" + "\n".join(missing_files)
        messagebox.showinfo("Erfolg", msg)

        if export_folder and os.path.isdir(export_folder):
            open_folder(export_folder)

if __name__ == "__main__":
    app = OBSAssetManagerGUI()
    app.mainloop()
