import ctypes
import os
import subprocess
import urllib.request
from pathlib import Path
import shutil
import winreg as reg

default_wallpaper = os.path.join(os.getenv('WINDIR'), 'Web', 'Wallpaper', 'Windows', 'img0.jpg')
downloaded_wallpaper_path = os.path.join(os.getenv("TEMP"), "downloaded_wallpaper.jpg")
UBLOCK_ORIGIN_URL = "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/addon-607454-latest.xpi"
DUCKDUCKGO_URL = "https://addons.mozilla.org/firefox/downloads/latest/duckduckgo-for-firefox/addon-618625-latest.xpi"
ZEN_BROWSER_URL = "https://github.com/zen-browser/desktop/releases/download/1.7b/zen.installer.exe"
downloads_folder = Path(os.path.expanduser("~")) / "Downloads"

def menu():
    print("\nWas möchten Sie ausführen?")
    print("1) Hintergrundbild setzen (herunterladen und anwenden)")
    print("2) Windows-Explorer neu starten")
    print("3) Visual Studio Code herunterladen und installieren")
    print("4) Zen Browser herunterladen und installieren")
    print("5) Firefox-Erweiterungen installieren (uBlock Origin & DuckDuckGo)")
    print("6) Darkmode aktivieren")
    print("7) Alles ausführen")
    print("8) Beenden")
    choice = input("Bitte wählen Sie eine Option (1-8): ")
    return choice

def download_file(url, save_path):
    try:
        print(f"Lade Datei von {url} herunter...")
        urllib.request.urlretrieve(url, save_path)
        print(f"Datei wurde heruntergeladen und unter '{save_path}' gespeichert.")
    except Exception as e:
        print(f"Fehler beim Herunterladen der Datei: {e}")

def set_wallpaper(image_path):
    if not os.path.isfile(image_path):
        print(f"Die Datei '{image_path}' existiert nicht.")
        return
    try:
        key = reg.HKEY_CURRENT_USER
        subkey = r"Control Panel\Desktop"
        reg_values = {
            "WallpaperStyle": "10",
            "TileWallpaper": "0"
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
    result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    if result == 0:
        print("Fehler beim Setzen des Hintergrunds.")
    else:
        print(f"Das Hintergrundbild wurde erfolgreich auf '{image_path}' gesetzt.")

def restart_explorer():
    print("Starte den Windows-Explorer neu...")
    try:
        subprocess.run("taskkill /f /im explorer.exe", shell=True, check=True)
        subprocess.run("explorer.exe", shell=True, check=True)
        print("Windows-Explorer wurde neu gestartet.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Neustarten des Windows Explorers: {e}")

def download_and_install_vscode():
    try:
        installer_path = downloads_folder / "VSCodeSetup.exe"
        url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
        print(f"Lade Visual Studio Code herunter von {url}...")
        download_file(url, installer_path)
        print("Installation von Visual Studio Code wird gestartet...")
        subprocess.run([installer_path, '/silent', '/mergetasks=!runcode'], check=True)
        print("Visual Studio Code wurde erfolgreich installiert.")
    except Exception as e:
        print(f"Fehler beim Herunterladen oder Installieren von Visual Studio Code: {e}")

def download_and_install_zen_browser():
    try:
        installer_path = downloads_folder / "zen_installer.exe"
        download_file(ZEN_BROWSER_URL, installer_path)
        if not os.path.isfile(installer_path):
            raise Exception(f"Der Zen Browser-Installer wurde nicht erfolgreich heruntergeladen: {installer_path}")
        print("Installation des Zen Browsers wird gestartet...")
        process = subprocess.Popen([installer_path, '/silent'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Zen Browser wurde erfolgreich installiert.")
        else:
            print(f"Fehler bei der Installation des Zen Browsers: {stderr.decode()}")
    except Exception as e:
        print(f"Fehler beim Herunterladen oder Installieren des Zen Browsers: {e}")

def enable_dark_mode():
    try:
        key = reg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value_name = "AppsUseLightTheme"
        with reg.OpenKey(key, subkey, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, 0)
        print("Der Dunkelmodus wurde aktiviert.")
        value_name = "SystemUsesLightTheme"
        with reg.OpenKey(key, subkey, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, 0)
        print("Die Taskleiste wurde auf den Dunkelmodus umgestellt.")
        restart_explorer()
    except Exception as e:
        print(f"Fehler beim Aktivieren des Dunkelmodus: {e}")

def install_firefox_addons():
    try:
        ublock_path = os.path.join(os.getenv("TEMP"), "ublock_origin.xpi")
        duckduckgo_path = os.path.join(os.getenv("TEMP"), "duckduckgo.xpi")
        download_file(UBLOCK_ORIGIN_URL, ublock_path)
        download_file(DUCKDUCKGO_URL, duckduckgo_path)
        firefox_profile_path = Path(os.getenv("APPDATA")) / "Mozilla" / "Firefox" / "Profiles"
        profiles = list(firefox_profile_path.glob("*.default*"))
        if not profiles:
            raise Exception("Keine Firefox-Profile gefunden.")
        for profile in profiles:
            extensions_dir = profile / "extensions"
            extensions_dir.mkdir(exist_ok=True)
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
            wallpaper_url = "https://raw.githubusercontent.com/Brokoli5191/stuff/refs/heads/main/tate_und_schnapsi_und_vinci.png"
            download_file(wallpaper_url, downloaded_wallpaper_path)
            set_wallpaper(downloaded_wallpaper_path)
        elif choice == "2":
            restart_explorer()
        elif choice == "3":
            download_and_install_vscode()
        elif choice == "4":
            download_and_install_zen_browser()
        elif choice == "5":
            install_firefox_addons()
        elif choice == "6":
            enable_dark_mode()
        elif choice == "7":
            wallpaper_url = "https://raw.githubusercontent.com/Brokoli5191/stuff/refs/heads/main/tate_und_schnapsi_und_vinci.png"
            download_file(wallpaper_url, downloaded_wallpaper_path)
            set_wallpaper(downloaded_wallpaper_path)
            enable_dark_mode()
            install_firefox_addons()
            restart_explorer()
        elif choice == "8":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Eingabe. Bitte wählen Sie eine Option von 1 bis 8.")
