#!/usr/bin/env python3
import zipfile
import rarfile
import py7zr
import tarfile
import time
from datetime import datetime
import os
import sys
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

class ArchiveCracker:
    def __init__(self):
        self.found = False
        self.stats = {
            'attempts': 0,
            'start_time': 0,
            'current_password': 'Starting...',
            'speed': 0,
            'progress': 0.0
        }
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Supported archive formats
        self.supported_formats = {
            '01': ('ZIP Archive', 'zip', self._try_zip),
            '02': ('RAR Archive', 'rar', self._try_rar),
            '03': ('7Z Archive', '7z', self._try_7z),
            '04': ('TAR Archive', 'tar', self._try_tar),
            '05': ('GZIP Archive', 'gz', self._try_gzip),
            '06': ('BZIP2 Archive', 'bz2', self._try_bzip2)
        }
        
        # Color schemes
        self.colors = {
            'header': Fore.YELLOW + Style.BRIGHT,
            'menu': Fore.CYAN + Style.BRIGHT,
            'option': Fore.GREEN + Style.BRIGHT,
            'prompt': Fore.CYAN + Style.BRIGHT,
            'success': Fore.GREEN + Style.BRIGHT,
            'error': Fore.RED + Style.BRIGHT,
            'warning': Fore.YELLOW + Style.BRIGHT,
            'info': Fore.BLUE + Style.BRIGHT,
            'progress': Fore.MAGENTA,
            'stats': Fore.CYAN,
            'password': Fore.WHITE + Back.BLACK + Style.BRIGHT,
            'highlight': Fore.BLACK + Back.WHITE + Style.BRIGHT
        }

    def signal_handler(self, sig, frame):
        """Handle CTRL+C gracefully"""
        print(f"\n{self.colors['error']}[!] Interrupted by user. Stopping...")
        self.display_stats()
        sys.exit(0)

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        """Display colorful banner with author info and description"""
        self.clear_screen()
        # Banner utama tanpa garis kotak
        banner = f"""
{Fore.RED}  ███████████  █████  █████ █████   ████   █████████  
{Fore.YELLOW}  ░░███░░░░░███░░███  ░░███ ░░███   ███░   ███░░░░░███ 
{Fore.GREEN}   ░███    ░███ ░███   ░███  ░███  ███    ░███    ░███ 
{Fore.CYAN}   ░██████████  ░███   ░███  ░███████     ░███████████ 
{Fore.BLUE}   ░███░░░░░███ ░███   ░███  ░███░░███    ░███░░░░░███ 
{Fore.MAGENTA}   ░███    ░███ ░███   ░███  ░███ ░░███   ░███    ░███ 
{Fore.WHITE}   ███████████  ░░████████   █████ ░░████ █████   █████
{Fore.BLACK}   ░░░░░░░░░░░    ░░░░░░░░   ░░░░░   ░░░░ ░░░░░   ░░░░░ 

"""
        info_box = f"""
{Fore.RED}╔══════════════════════════════════════════╗
{Fore.RED}║ {self.colors['header']} Archive Password BruteForce Tool        {Fore.RED}║
{Fore.RED}╠══════════════════════════════════════════╣
{Fore.RED}║ {Fore.WHITE} Author: East Timor Ghost Security       {Fore.RED}║
{Fore.RED}║ {Fore.WHITE} Version: 1.1                            {Fore.RED}║
{Fore.RED}╚══════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner + info_box)

    def select_archive_type(self):
        """Show archive type selection menu"""
        self.show_banner()
        print(f"{self.colors['menu']}Select archive type:\n")
        for code, (name, ext, _) in self.supported_formats.items():
            print(f"{self.colors['option']}[{code}] {name} (.{ext})")
        print(f"{self.colors['option']}[99] Exit\n")
        while True:
            choice = input(f"{self.colors['prompt']}[?] Select option: ").strip()
            if choice in self.supported_formats:
                return self.supported_formats[choice]
            elif choice == '99':
                sys.exit(0)
            else:
                print(f"{self.colors['error']}[!] Invalid choice. Please try again.")

    def get_user_input(self, archive_type, ext):
        """Get archive file and wordlist from user"""
        self.show_banner()
        print(f"{self.colors['info']}[+] Selected: {archive_type} (.{ext})\n")
        while True:
            archive_path = input(f"{self.colors['prompt']}[?] Path to .{ext} file: ").strip()
            if not os.path.exists(archive_path):
                print(f"{self.colors['error']}[!] File not found. Please try again.")
                continue
            if not archive_path.lower().endswith(f'.{ext}'):
                print(f"{self.colors['warning']}[!] File extension doesn't match {ext} format")
                confirm = input(f"{self.colors['prompt']}[?] Continue anyway? (y/N): ").lower()
                if confirm != 'y':
                    continue
            break
        while True:
            wordlist = input(f"{self.colors['prompt']}[?] Path to wordlist: ").strip()
            if os.path.exists(wordlist):
                break
            print(f"{self.colors['error']}[!] File not found. Please try again.")
        while True:
            try:
                threads = input(f"{self.colors['prompt']}[?] Threads to use (1-16, default=4): ").strip()
                threads = int(threads) if threads else 4
                if 1 <= threads <= 16:
                    break
                print(f"{self.colors['error']}[!] Please enter value between 1-16")
            except ValueError:
                print(f"{self.colors['error']}[!] Invalid number")
        return archive_path, wordlist, threads

    def _try_zip(self, archive_path, password):
        """Test password against ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(pwd=password.encode('utf-8'))
            return True
        except:
            return False

    def _try_rar(self, archive_path, password):
        """Test password against RAR archive"""
        try:
            with rarfile.RarFile(archive_path) as archive:
                archive.extractall(pwd=password)
            return True
        except:
            return False

    def _try_7z(self, archive_path, password):
        """Test password against 7Z archive"""
        try:
            with py7zr.SevenZipFile(archive_path, password=password) as archive:
                archive.extractall()
            return True
        except:
            return False

    def _try_tar(self, archive_path, password):
        """Test password against TAR archive"""
        try:
            with tarfile.open(archive_path) as archive:
                archive.extractall()
            return True
        except:
            return False

    def _try_gzip(self, archive_path, password):
        """Test password against GZIP archive"""
        try:
            with tarfile.open(archive_path, 'r:gz') as archive:
                archive.extractall()
            return True
        except:
            return False

    def _try_bzip2(self, archive_path, password):
        """Test password against BZIP2 archive"""
        try:
            with tarfile.open(archive_path, 'r:bz2') as archive:
                archive.extractall()
            return True
        except:
            return False

    def check_dependencies(self, ext):
        """Check if required dependencies are installed"""
        if ext == 'rar':
            try:
                import rarfile
            except ImportError:
                print(f"\n{self.colors['error']}[!] RAR support requires 'rarfile' and 'unrar'.")
                print(f"{self.colors['info']}[+] Please install with: {Fore.WHITE}pip install rarfile")
                print(f"{self.colors['info']}[+] On Linux, also install: {Fore.WHITE}sudo apt install unrar")
                sys.exit(1)
        if ext == '7z':
            try:
                import py7zr
            except ImportError:
                print(f"\n{self.colors['error']}[!] 7Z support requires 'py7zr'.")
                print(f"{self.colors['info']}[+] Please install with: {Fore.WHITE}pip install py7zr")
                sys.exit(1)

    def _count_lines(self, file_path):
        """Count lines in a file efficiently"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def update_display(self, total_passwords):
        """Update the display with current password being tested"""
        elapsed = time.time() - self.stats['start_time']
        speed = self.stats['attempts'] / elapsed if elapsed > 0 else 0
        anim_char = "|/-\\"[self.stats['attempts'] % 4]
        # Calculate progress percentage
        progress = (self.stats['attempts'] / total_passwords) * 100 if total_passwords > 0 else 0
        # Create progress bar
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = f"{Fore.GREEN}█" * filled + f"{Fore.WHITE}░" * (bar_length - filled)
        # Display current password being tried
        print(f"\r{self.colors['progress']}[+] Testing: {Fore.YELLOW}{anim_char} "
              f"{self.colors['password']}{self.stats['current_password']:<25} "
              f"{self.colors['stats']}Progress: {bar} {progress:.1f}% "
              f"{self.colors['stats']}Speed: {Fore.WHITE}{speed:.1f}/sec", 
              end="", flush=True)

    def run_attack(self, archive_path, wordlist_path, test_func, threads=4):
        """Execute the password attack with multithreading"""
        self.show_banner()
        print(f"{self.colors['info']}[+] Target: {Fore.WHITE}{archive_path}")
        print(f"{self.colors['info']}[+] Wordlist: {Fore.WHITE}{wordlist_path}")
        print(f"{self.colors['info']}[+] Threads: {Fore.WHITE}{threads}\n")
        self.stats['start_time'] = time.time()
        total_passwords = self._count_lines(wordlist_path)
        found_password = None
        try:
            # Read all passwords into memory for accurate progress tracking
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
                total_passwords = len(passwords)
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = []
                    for password in passwords:
                        if self.found:
                            break
                        # Update current password before testing
                        self.stats['current_password'] = password
                        self.stats['attempts'] += 1
                        # Submit password test to thread pool
                        futures.append(executor.submit(
                            self._test_password_wrapper, 
                            test_func, 
                            archive_path, 
                            password
                        ))
                        # Update display after each password submission
                        self.update_display(total_passwords)
                    # Check results as they complete
                    for future in as_completed(futures):
                        if future.result():
                            self.found = True
                            found_password = future.result()
                            break
            return found_password
        except Exception as e:
            print(f"\n{self.colors['error']}[!] Error: {str(e)}")
            return None

    def _test_password_wrapper(self, test_func, archive_path, password):
        """Wrapper for password testing that returns password if successful"""
        if test_func(archive_path, password):
            return password
        return None

    def display_stats(self):
        """Show final statistics"""
        elapsed = time.time() - self.stats['start_time']
        print(f"\n{self.colors['header']}[+] Attack summary:")
        print(f"{self.colors['stats']}[+] {Fore.WHITE}Runtime: {Fore.CYAN}{elapsed:.2f} seconds")
        print(f"{self.colors['stats']}[+] {Fore.WHITE}Total attempts: {Fore.CYAN}{self.stats['attempts']}")
        if elapsed > 0:
            print(f"{self.colors['stats']}[+] {Fore.WHITE}Average speed: {Fore.CYAN}{self.stats['attempts']/elapsed:.1f} attempts/sec")

    def save_result(self, archive_path, password):
        """Save successful result to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recovered_password_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Archive: {archive_path}\n")
            f.write(f"Password: {password}\n")
            f.write(f"Found at: {datetime.now().isoformat()}\n")
            f.write(f"Attempts: {self.stats['attempts']}\n")
            f.write(f"Duration: {time.time() - self.stats['start_time']:.2f} seconds\n")
        print(f"{self.colors['info']}[+] Results saved to: {Fore.WHITE}{filename}")

    def run(self):
        """Main execution flow"""
        archive_type, ext, test_func = self.select_archive_type()
        self.check_dependencies(ext)
        archive_path, wordlist_path, threads = self.get_user_input(archive_type, ext)
        password = self.run_attack(archive_path, wordlist_path, test_func, threads)
        if password:
            print(f"\n{self.colors['success']}[+] {Fore.WHITE}SUCCESS! Password found: {self.colors['password']}{password}")
            self.save_result(archive_path, password)
        else:
            print(f"\n{self.colors['warning']}[-] {Fore.WHITE}Password not found in the wordlist")
        self.display_stats()

if __name__ == "__main__":
    cracker = ArchiveCracker()
    cracker.run()

