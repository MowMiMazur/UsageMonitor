###############################################
#     _____ _____ _____ _____ _____ _____     #
#    |     |  _  |__   |   | |   __|_   _|    #
#    | | | |     |   __| | | |   __| | |      #
#    |_|_|_|__|__|_____|_|___|_____| |_|      #
#                                             #
#          Copyright (c) 2026 MAZNET          #
#       Author: MAZNET (Mateusz Mazur)        #
#                                             #
###############################################


# ============================================================
# IMPORTY
# ============================================================
import psutil
import time
from statistics import mean
from PySide6.QtCore import QThread, Signal

# ============================================================
# MONITOROWANIE PROCESU
# ============================================================
class MonitorThread(QThread):
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, pid, output_file, interval=1):
        super().__init__()
        self.pid = pid
        self.output_file = output_file
        self.interval = interval
        self._is_running = True
        
        self.cpu_raw_samples = []
        self.cpu_norm_samples = []
        self.ram_samples = []
        self.cpu_count = psutil.cpu_count(logical=True)
        
        self.start_time = None
        self.end_time = None

    def run(self):
        try:
            process = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            self.error.emit(f"Proces o PID {self.pid} nie istnieje lub zakończył działanie.")
            return

        self.start_time = time.time()
        
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("timestamp,cpu_raw_percent,cpu_normalized_percent,ram_mb\n")
                
                # === Inicjalizacja licznika CPU ===
                process.cpu_percent(interval=None)

                while self._is_running:
                    if not process.is_running():
                        break

                    try:
                        cpu_raw = process.cpu_percent(interval=None)
                        cpu_norm = cpu_raw / self.cpu_count
                        ram = process.memory_info().rss / (1024 * 1024)

                        self.cpu_raw_samples.append(cpu_raw)
                        self.cpu_norm_samples.append(cpu_norm)
                        self.ram_samples.append(ram)

                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(
                            f"{timestamp},"
                            f"{cpu_raw:.2f},"
                            f"{cpu_norm:.2f},"
                            f"{ram:.2f}\n"
                        )
                        f.flush()
                        
                        # === Czekaj z możliwością wcześniejszego przerwania ===
                        for _ in range(int(self.interval * 10)):
                            if not self._is_running:
                                break
                            time.sleep(0.1)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
        except Exception as e:
            self.error.emit(str(e))
            return

        self.end_time = time.time()
        self.compute_stats()

    # === Metoda do zatrzymania monitorowania ===
    def stop(self):
        self._is_running = False

    # === Obliczanie statystyk po zakończeniu monitorowania ===
    def compute_stats(self):
        stats_data = {}
        
        # === Funkcja pomocnicza do obliczania min, max, średniej ===
        def calculate(values):
            if not values:
                return 0.0, 0.0, 0.0
            return min(values), max(values), mean(values)

        if self.cpu_raw_samples:
            cpu_raw_stats = calculate(self.cpu_raw_samples)
            cpu_norm_stats = calculate(self.cpu_norm_samples)
            ram_stats = calculate(self.ram_samples)

            stats_data['cpu_raw'] = cpu_raw_stats
            stats_data['cpu_norm'] = cpu_norm_stats
            stats_data['ram'] = ram_stats
            
            # === Przekazanie próbek do wykresów ===
            stats_data['samples'] = {
                'cpu_raw': self.cpu_raw_samples,
                'cpu_norm': self.cpu_norm_samples,
                'ram': self.ram_samples
            }
            
            stats_data['has_data'] = True
            stats_data['output_file'] = self.output_file

            # === Obliczanie czasów ===
            start_ts = self.start_time if self.start_time else 0
            end_ts = self.end_time if self.end_time else time.time()
            duration_seconds = end_ts - start_ts
            
            start_str = time.strftime("%H:%M:%S", time.localtime(start_ts))
            end_str = time.strftime("%H:%M:%S", time.localtime(end_ts))
            
            m, s = divmod(int(duration_seconds), 60)
            h, m = divmod(m, 60)
            duration_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"

            stats_data['start_str'] = start_str
            stats_data['end_str'] = end_str
            stats_data['duration_str'] = duration_str

            # === Zapisz podsumowanie do pliku ===
            try:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write("=" * 40 + "\n")
                    f.write("           PODSUMOWANIE SESJI\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"Start: {start_str} | Koniec: {end_str} | Czas: {duration_str}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"CPU (Raw):   Min: {cpu_raw_stats[0]:6.2f}% | Max: {cpu_raw_stats[1]:6.2f}% | Śr: {cpu_raw_stats[2]:6.2f}%\n")
                    f.write(f"CPU (Norm):  Min: {cpu_norm_stats[0]:6.2f}% | Max: {cpu_norm_stats[1]:6.2f}% | Śr: {cpu_norm_stats[2]:6.2f}%\n")
                    f.write(f"RAM:         Min: {ram_stats[0]:6.2f} MB | Max: {ram_stats[1]:6.2f} MB | Śr: {ram_stats[2]:6.2f} MB\n")
                    f.write("=" * 40 + "\n")
            except Exception as e:
                # Nie chcemy, aby błąd zapisu statystyk przerwał działanie programu
                print(f"Błąd podczas zapisywania statystyk do pliku: {e}")

        else:
            stats_data['has_data'] = False
            
        self.finished.emit(stats_data)
