import ctypes
import os
import subprocess
import urllib.request
from pathlib import Path
import shutil
import winreg as reg

# Standard-Hintergrundbild (Windows-Standard)
default_wallpaper = os.path.join(os.getenv('WINDIR'), 'Web', 'Wallpaper', 'Windows', 'img0.jpg')

# Pfad, um das heruntergeladene Hintergrundbild zu speichern
downloaded_wallpaper_path = os.path.join(os.getenv("TEMP"), "downloaded_wallpaper.jpg")

# URLs der Add-ons
UBLOCK_ORIGIN_URL = "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/addon-607454-latest.xpi"
DUCKDUCKGO_URL = "https://addons.mozilla.org/firefox/downloads/latest/duckduckgo-for-firefox/addon-618625-latest.xpi"

# Menü zur Auswahl der Aktionen
def menu():
    print("\nWas möchten Sie ausführen?")
    print("1) Hintergrundbild setzen (herunterladen und anwenden)")
    print("2) Windows-Explorer neu starten")
    print("3) Visual Studio Code herunterladen und installieren")
    print("4) Firefox-Erweiterungen installieren (uBlock Origin & DuckDuckGo)")
    print("5) Darkmode aktivieren")
    print("6) Alles ausführen")
    print("7) Beenden")

    choice = input("Bitte wählen Sie eine Option (1-7): ")
    return choice

# Funktion zum Herunterladen einer Datei
def download_file(url, save_path):
    try:
        print(f"Lade Datei von {url} herunter...")
        urllib.request.urlretrieve(url, save_path)
        print(f"Datei wurde heruntergeladen und unter '{save_path}' gespeichert.")
    except Exception as e:
        print(f"Fehler beim Herunterladen der Datei: {e}")

# Funktion zum Setzen des Hintergrundbilds
def set_wallpaper(image_path):
    if not os.path.isfile(image_path):
        print(f"Die Datei '{image_path}' existiert nicht.")
        return
    
    # Setzt die Skalierungsoptionen in der Registry auf "Fill" (füllen)
    try:
        key = reg.HKEY_CURRENT_USER
        subkey = r"Control Panel\Desktop"
        reg_values = {
            "WallpaperStyle": "10",  # 10 = Fill
            "TileWallpaper": "0"     # 0 = Nicht kacheln
        }
        with reg.OpenKey(key, subkey, 0, reg.KEY_WRITE) as registry_key:
            for value_name, value in reg_values.items():
                reg.SetValueEx(registry_key, value_name, 0, reg.REG_SZ, value)
        
        print("Skalierung auf 'Füllen' gesetzt.")
    except Exception as e:
        print(f"Fehler beim Setzen der Skalierungsoptionen: {e}")
    
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x1
    SPIF_SENDCHANGE = 0x2
    
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

    if result == 0:
        print("Fehler beim Setzen des Hintergrunds.")
    else:
        print(f"Das Hintergrundbild wurde erfolgreich auf '{image_path}' gesetzt.")

# Funktion zum Neustarten des Explorers
def restart_explorer():
    print("Starte den Windows-Explorer neu...")
    try:
        subprocess.run("taskkill /f /im explorer.exe", shell=True, check=True)
        subprocess.run("explorer.exe", shell=True, check=True)
        print("Windows-Explorer wurde neu gestartet.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Neustarten des Windows Explorers: {e}")

# Funktion zum Herunterladen und Installieren von Visual Studio Code
def download_and_install_vscode():
    try:
        url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
        installer_path = os.path.join(os.getenv("TEMP"), "VSCodeSetup.exe")
        
        print(f"Lade Visual Studio Code herunter von {url}...")
        urllib.request.urlretrieve(url, installer_path)
        
        print("Installation von Visual Studio Code wird gestartet...")
        subprocess.run([installer_path, '/silent', '/mergetasks=!runcode'], check=True)
        print("Visual Studio Code wurde erfolgreich installiert.")
    except Exception as e:
        print(f"Fehler beim Herunterladen oder Installieren von Visual Studio Code: {e}")
        
# Funktion zum Aktivieren des Darkmodes
def enable_dark_mode():
    try:
        key = reg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value_name = "AppsUseLightTheme"

        # Öffnen des Registrierungsschlüssels
        with reg.OpenKey(key, subkey, 0, reg.KEY_WRITE) as registry_key:
            # Setze den Wert auf 0 für Dunkelmodus
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, 0)
        
        print("Der Dunkelmodus wurde aktiviert.")
        
        # Die Taskleiste und Fenster in den Dark Mode versetzen
        value_name = "SystemUsesLightTheme"
        with reg.OpenKey(key, subkey, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, 0)
        
        print("Die Taskleiste wurde auf den Dunkelmodus umgestellt.")
        
        # Neustart des Windows-Explorers, um die Änderungen sofort zu übernehmen
        restart_explorer()
    
    except Exception as e:
        print(f"Fehler beim Aktivieren des Dunkelmodus: {e}")

# Funktion zum Installieren von Firefox-Add-ons in allen Profilen
def install_firefox_addons():
    try:
        # Download-Pfade für Add-ons
        ublock_path = os.path.join(os.getenv("TEMP"), "ublock_origin.xpi")
        duckduckgo_path = os.path.join(os.getenv("TEMP"), "duckduckgo.xpi")

        # Add-ons herunterladen
        download_file(UBLOCK_ORIGIN_URL, ublock_path)
        download_file(DUCKDUCKGO_URL, duckduckgo_path)

        # Firefox-Profile finden
        firefox_profile_path = Path(os.getenv("APPDATA")) / "Mozilla" / "Firefox" / "Profiles"
        profiles = list(firefox_profile_path.glob("*.default*"))

        if not profiles:
            raise Exception("Keine Firefox-Profile gefunden.")

        for profile in profiles:
            extensions_dir = profile / "extensions"
            extensions_dir.mkdir(exist_ok=True)

            # Add-ons kopieren
            shutil.copy(ublock_path, extensions_dir / "uBlock0@raymondhill.net.xpi")
            shutil.copy(duckduckgo_path, extensions_dir / "ddg@duckduckgo.com.xpi")
            print(f"Add-ons wurden in das Profil '{profile.name}' installiert.")

        print("Alle Add-ons wurden erfolgreich installiert. Bitte starten Sie Firefox neu.")
    except Exception as e:
        print(f"Fehler beim Installieren der Add-ons: {e}")

if __name__ == "__main__":
    while True:
        choice = menu()
        if choice == "1":
            wallpaper_url = "https://raw.githubusercontent.com/Brokoli5191/stuff/refs/heads/main/wallpaper.jpg"
            download_file(wallpaper_url, downloaded_wallpaper_path)
            set_wallpaper(downloaded_wallpaper_path)
        elif choice == "2":
            restart_explorer()
        elif choice == "3":
            download_and_install_vscode()
        elif choice == "4":
            install_firefox_addons()
        elif choice == "5":
            enable_dark_mode()
        elif choice == "6":
            wallpaper_url = "https://raw.githubusercontent.com/Brokoli5191/stuff/refs/heads/main/wallpaper.jpg"
            download_file(wallpaper_url, downloaded_wallpaper_path)
            set_wallpaper(downloaded_wallpaper_path)
            enable_dark_mode()
            install_firefox_addons()
            restart_explorer()
        elif choice == "7":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Eingabe. Bitte wählen Sie eine Option von 1 bis 7.")
