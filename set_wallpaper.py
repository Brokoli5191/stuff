import os
import ctypes
import time
import winreg as reg
import urllib.request
import shutil

# URL des Bildes
bild_url = "https://github.com/Brokoli5191/stuff/blob/main/tate_und_schnapsi_und_vinci.png?raw=true"
bild_path = os.path.join(os.getenv('TEMP'), "downloaded_image.png")

# Hintergrundbild einstellen
def set_wallpaper(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

# Dark Mode aktivieren (über die Registry)
def enable_dark_mode():
    try:
        key = reg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value_name = "AppsUseLightTheme"

        with reg.OpenKey(key, subkey, 0, reg.KEY_SET_VALUE) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, 0)
        
        print("Darkmode wurde aktiviert.")
    except Exception as e:
        print(f"Fehler beim Aktivieren des Darkmodes: {e}")

# Akzentfarbe auf Rot setzen (über die Registry)
def set_accent_color():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Control Panel\Colors", 0, reg.KEY_WRITE)
        reg.SetValueEx(key, "AccentColor", 0, reg.REG_SZ, "255 0 0")  # RGB für Rot
        reg.CloseKey(key)
        print("Akzentfarbe auf Rot gesetzt")
    except Exception as e:
        print(f"Fehler beim Setzen der Akzentfarbe: {e}")

# Bild herunterladen
def download_image(url, save_path):
    try:
        print("Lade Bild herunter...")
        urllib.request.urlretrieve(url, save_path)
        print(f"Bild erfolgreich heruntergeladen: {save_path}")
    except Exception as e:
        print(f"Fehler beim Herunterladen des Bildes: {e}")

# Windows Explorer neu starten
def restart_explorer():
    try:
        os.system('taskkill /f /im explorer.exe')
        time.sleep(1)  # Warten, damit Explorer vollständig beendet wird
        os.system('start explorer.exe')
        print("Windows Explorer wurde neu gestartet.")
    except Exception as e:
        print(f"Fehler beim Neustarten des Explorers: {e}")

# Hauptfunktion
def main():
    # Bild herunterladen
    download_image(bild_url, bild_path)
    
    # Hintergrundbild setzen
    set_wallpaper(bild_path)
    print("Hintergrundbild gesetzt.")
    
    # Dark Mode aktivieren
    enable_dark_mode()
    
    # Akzentfarbe auf Rot setzen
    set_accent_color()

    # Windows Explorer neu starten
    restart_explorer()

    print("Alle Einstellungen wurden erfolgreich vorgenommen.")

if __name__ == "__main__":
    main()
