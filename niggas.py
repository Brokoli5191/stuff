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
    
    def download_zen_browser(self):
        """Lädt die neueste Zen Browser-Version herunter und startet die Installation"""
        try:
            print("Lade neueste Zen Browser-Version herunter...")
            
            # Zen Browser Download URL (automatisch neueste Version)
            zen_url = "https://zen-browser.app/download/windows/x64"
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            zen_installer = os.path.join(downloads_folder, "ZenBrowserInstaller.exe")
            
            # Download Zen Browser Installer
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(zen_url, headers=headers, stream=True, allow_redirects=True)
            response.raise_for_status()
            
            with open(zen_installer, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Zen Browser Installer heruntergeladen: {zen_installer}")
            
            # Starte Zen Browser Installation
            print("Starte Zen Browser Installation...")
            try:
                subprocess.Popen([zen_installer])
                print("✓ Zen Browser Installer geöffnet - folge den Anweisungen zur Installation")
            except Exception as e:
                print(f"Zen Browser Installer wurde heruntergeladen nach: {zen_installer}")
                print("Bitte führe die Installation manuell aus.")
                
            return True
            
        except Exception as e:
            print(f"✗ Fehler beim Herunterladen von Zen Browser: {e}")
            print("Fallback: Versuche alternative Download-Methode...")
            
            # Fallback: GitHub Releases API
            try:
                api_url = "https://api.github.com/repos/zen-browser/desktop/releases/latest"
                response = requests.get(api_url)
                response.raise_for_status()
                
                release_data = response.json()
                
                # Suche nach Windows x64 Installer
                for asset in release_data.get('assets', []):
                    if 'windows' in asset['name'].lower() and 'x64' in asset['name'].lower():
                        download_url = asset['browser_download_url']
                        
                        print(f"Lade {asset['name']} herunter...")
                        response = requests.get(download_url, stream=True)
                        response.raise_for_status()
                        
                        zen_installer = os.path.join(downloads_folder, asset['name'])
                        with open(zen_installer, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"✓ Zen Browser von GitHub heruntergeladen: {zen_installer}")
                        subprocess.Popen([zen_installer])
                        return True
                
                print("✗ Kein passender Windows-Installer gefunden")
                return False
                
            except Exception as fallback_error:
                print(f"✗ Auch Fallback-Download fehlgeschlagen: {fallback_error}")
                print("Bitte lade Zen Browser manuell von https://zen-browser.app herunter")
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
            
            # Download des Bildes
            wallpaper_path = os.path.join(os.path.expanduser("~"), "Downloads", "wallpaper.jpg")
            
            response = requests.get(wallpaper_url)
            response.raise_for_status()
            
            with open(wallpaper_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Hintergrundbild heruntergeladen: {wallpaper_path}")
            return wallpaper_path
            
        except Exception as e:
            print(f"✗ Fehler beim Herunterladen des Hintergrundbildes: {e}")
            return None
    
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
        
        print("\n=== Setup abgeschlossen! ===")
        print("Hinweise:")
        print("- Dark Mode wurde aktiviert (evtl. Neustart erforderlich)")
        print("- Zen Browser Installer wurde gestartet - folge den Installationsschritten")
        print("- Hintergrundbild wurde gesetzt")

def main():
    setup = WindowsSetup()
    
    # Du kannst hier das GitHub Repository für Hintergrundbilder ändern
    github_repo = "microsoft/terminal"  # Ändere dies nach Bedarf
    
    setup.run_setup(github_repo)

if __name__ == "__main__":
    main()