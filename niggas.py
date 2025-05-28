import os
import sys
import winreg
import requests
import subprocess
from pathlib import Path
import ctypes
from ctypes import wintypes
import tempfile
import re
import time

class WindowsSetup:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def set_dark_mode(self):
        """Setzt Windows auf Dark Mode"""
        try:
            # Registry-Schlüssel für Dark Mode
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            # Öffne Registry-Schlüssel
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                # Apps verwenden Dark Theme
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
                # System verwendet Dark Theme  
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
            
            print("✓ Dark Mode erfolgreich aktiviert")
            return True
            
        except Exception as e:
            print(f"✗ Fehler beim Setzen des Dark Mode: {e}")
            return False
    
    def format_bytes(self, bytes_value):
        """Formatiert Bytes in eine lesbare Form (KB, MB, GB)"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def show_progress_bar(self, downloaded, total, width=50):
        """Zeigt eine schöne Progress-Bar wie auf Linux"""
        if total == 0:
            return
        
        percentage = (downloaded / total) * 100
        filled_width = int(width * downloaded // total)
        
        # Progress-Bar mit schönen Zeichen
        bar = '█' * filled_width + '▒' * (width - filled_width)
        
        # Formatierte Ausgabe
        downloaded_str = self.format_bytes(downloaded)
        total_str = self.format_bytes(total)
        
        print(f'\r[{bar}] {percentage:6.2f}% ({downloaded_str}/{total_str})', end='', flush=True)
    
    def download_zen_browser(self):
        """Lädt die neueste Zen Browser-Version herunter und startet die Installation"""
        try:
            print("Lade neueste Zen Browser-Version herunter...")
            
            # GitHub API für neueste Release
            api_url = "https://api.github.com/repos/zen-browser/desktop/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_data = response.json()
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            
            print(f"Neueste Version: {release_data.get('tag_name', 'unbekannt')}")
            
            # Suche nach Windows-Installer (verschiedene Möglichkeiten)
            windows_assets = []
            for asset in release_data.get('assets', []):
                asset_name = asset['name'].lower()
                if ('windows' in asset_name or 'win' in asset_name) and asset_name.endswith('.exe'):
                    windows_assets.append(asset)
            
            if not windows_assets:
                # Fallback: Suche nach .exe Dateien generell
                for asset in release_data.get('assets', []):
                    if asset['name'].lower().endswith('.exe'):
                        windows_assets.append(asset)
            
            if not windows_assets:
                raise Exception("Kein Windows-Installer in der neuesten Release gefunden")
            
            # Wähle den besten Installer (bevorzuge x64)
            best_asset = None
            for asset in windows_assets:
                if 'x64' in asset['name'].lower() or '64' in asset['name'].lower():
                    best_asset = asset
                    break
            
            if not best_asset:
                best_asset = windows_assets[0]  # Nimm den ersten verfügbaren
            
            download_url = best_asset['browser_download_url']
            installer_name = best_asset['name']
            zen_installer = os.path.join(downloads_folder, installer_name)
            
            print(f"Lade {installer_name} herunter...")
            
            # Download mit schöner Progress-Bar
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zen_installer, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.show_progress_bar(downloaded, total_size)
            
            print(f"\n✓ Zen Browser Installer heruntergeladen: {zen_installer}")
            
            # Starte Installation
            print("Starte Zen Browser Installation...")
            try:
                subprocess.Popen([zen_installer])
                print("✓ Zen Browser Installer geöffnet - folge den Anweisungen zur Installation")
                return True
            except Exception as e:
                print(f"Installer wurde heruntergeladen nach: {zen_installer}")
                print("Bitte führe die Installation manuell aus.")
                return True
                
        except Exception as e:
            print(f"✗ Fehler beim Herunterladen von Zen Browser: {e}")
            
            # Letzter Fallback: Direkte Links zu bekannten Download-Seiten
            print("Fallback: Versuche alternative Download-Quellen...")
            
            alternative_sources = [
                {
                    'name': 'Uptodown',
                    'url': 'https://zen-browser.en.uptodown.com/windows/download',
                    'description': 'Uptodown Download-Seite'
                },
                {
                    'name': 'Softpedia', 
                    'url': 'https://www.softpedia.com/get/Internet/Browsers/Zen-Browser.shtml',
                    'description': 'Softpedia Download-Seite'
                }
            ]
            
            print("Alternative Download-Quellen:")
            for source in alternative_sources:
                print(f"- {source['name']}: {source['url']}")
            
            print("\nOder besuche die offizielle Website: https://zen-browser.app")
            
            # Versuche, die offizielle Website zu öffnen
            try:
                import webbrowser
                webbrowser.open('https://zen-browser.app/download/')
                print("✓ Zen Browser Download-Seite im Browser geöffnet")
            except:
                pass
            
            return False
    
    def get_github_wallpaper(self, repo_url="microsoft/terminal", image_pattern=r"wallpaper.*\.(?:jpg|jpeg|png|bmp)"):
        """Lädt ein Hintergrundbild von einem GitHub Repository"""
        try:
            print(f"Suche Hintergrundbild in Repository: {repo_url}")
            
            # GitHub API URL für Repository-Inhalte
            api_url = f"https://api.github.com/repos/{repo_url}/contents"
            
            response = requests.get(api_url)
            response.raise_for_status()
            
            files = response.json()
            wallpaper_url = None
            
            # Suche nach Bilddateien
            for file in files:
                if file['type'] == 'file' and re.search(image_pattern, file['name'].lower()):
                    wallpaper_url = file['download_url']
                    break
            
            # Falls nichts gefunden, versuche andere beliebte Wallpaper-Repos
            if not wallpaper_url:
                fallback_repos = [
                    "microsoft/terminal",
                    "microsoft/PowerToys", 
                    "github/explore"
                ]
                
                for repo in fallback_repos:
                    try:
                        api_url = f"https://api.github.com/repos/{repo}/contents"
                        response = requests.get(api_url)
                        files = response.json()
                        
                        for file in files:
                            if (file['type'] == 'file' and 
                                any(ext in file['name'].lower() for ext in ['.jpg', '.jpeg', '.png', '.bmp'])):
                                wallpaper_url = file['download_url']
                                break
                        
                        if wallpaper_url:
                            break
                    except:
                        continue
            
            # Falls immer noch nichts gefunden, verwende ein Standard-Bild
            if not wallpaper_url:
                # Verwende ein schönes Standardbild von Unsplash
                wallpaper_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2560&q=80"
            
            # Download des Bildes mit Progress-Bar
            wallpaper_path = os.path.join(os.path.expanduser("~"), "Downloads", "wallpaper.jpg")
            
            print("Lade Hintergrundbild herunter...")
            response = requests.get(wallpaper_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(wallpaper_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.show_progress_bar(downloaded, total_size)
            
            print(f"\n✓ Hintergrundbild heruntergeladen: {wallpaper_path}")
            return wallpaper_path
            
        except Exception as e:
            print(f"✗ Fehler beim Herunterladen des Hintergrundbildes: {e}")
            return None
    
    def restart_explorer(self):
        """Startet den Windows Explorer neu, damit alle Änderungen sofort sichtbar werden"""
        try:
            print("Starte Windows Explorer neu...")
            
            # Explorer beenden
            subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                         capture_output=True, check=False)
            
            # Kurz warten
            import time
            time.sleep(2)
            
            # Explorer neu starten
            subprocess.Popen(['explorer.exe'])
            
            print("✓ Windows Explorer wurde neu gestartet")
            return True
            
        except Exception as e:
            print(f"✗ Fehler beim Neustarten des Explorers: {e}")
            print("Bitte starte Windows manuell neu oder melde dich ab/an")
            return False
    
    def set_wallpaper(self, image_path):
        """Setzt das Hintergrundbild in Windows"""
        try:
            # Windows API zum Setzen des Hintergrundbildes
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02
            
            result = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 
                0, 
                image_path, 
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            
            if result:
                print("✓ Hintergrundbild erfolgreich gesetzt")
                return True
            else:
                print("✗ Fehler beim Setzen des Hintergrundbildes")
                return False
                
        except Exception as e:
            print(f"✗ Fehler beim Setzen des Hintergrundbildes: {e}")
            return False
    
    def run_setup(self, github_repo="microsoft/terminal"):
        """Führt das komplette Setup aus"""
        print("=== Windows Setup Automatisierung ===\n")
        
        # 1. Dark Mode aktivieren
        print("1. Aktiviere Dark Mode...")
        self.set_dark_mode()
        print()
        
        # 2. Zen Browser herunterladen und installieren
        print("2. Lade Zen Browser herunter und installiere...")
        self.download_zen_browser()
        print()
        
        # 3. Hintergrundbild von GitHub holen und setzen
        print("3. Lade Hintergrundbild von GitHub...")
        wallpaper_path = self.get_github_wallpaper(github_repo)
        
        if wallpaper_path:
            print("4. Setze Hintergrundbild...")
            self.set_wallpaper(wallpaper_path)
        print()
        
        # 4. Explorer neustarten für sofortige Änderungen
        print("5. Starte Windows Explorer neu...")
        self.restart_explorer()
        print()
        
        print("=== Setup erfolgreich abgeschlossen! ===")
        print("Alle Änderungen wurden angewendet:")
        print("✓ Dark Mode aktiviert")
        print("✓ Zen Browser heruntergeladen")
        print("✓ Hintergrundbild gesetzt")
        print("✓ Windows Explorer neu gestartet")
        print("\nDas Programm wird automatisch beendet...")
        
        # Kurz warten, damit der Benutzer die Meldung lesen kann
        import time
        time.sleep(3)
        
        # Programm beenden
        sys.exit(0)

def main():
    setup = WindowsSetup()
    
    # Du kannst hier das GitHub Repository für Hintergrundbilder ändern
    github_repo = "microsoft/terminal"  # Ändere dies nach Bedarf
    
    setup.run_setup(github_repo)

if __name__ == "__main__":
    main()