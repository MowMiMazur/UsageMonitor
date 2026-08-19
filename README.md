<a name="top"></a>
<div align="center">

<p align="center">
  <img src="assets/icon.png" alt="UsageMonitor" width="90" />
</p>

<h1 align="center">UsageMonitor</h1>

**Monitor CPU i RAM dowolnego procesu w czasie rzeczywistym**<br />
**Real-time CPU &amp; RAM monitor for any process**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-pywebview%20%2F%20WebView2-2ea043?logo=googlechrome&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-Apache--2.0-brightgreen)

### [🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

</div>

---

## Polski

Niewielki rdzeń w Pythonie z interfejsem w całości opartym na technologiach webowych (HTML/CSS/JS),
renderowanym w natywnym oknie.

### Opis

Wskaż UsageMonitorowi działający proces (po identyfikatorze PID albo wybierając go z listy) i obserwuj
zużycie CPU oraz RAM na żywo. Po zatrzymaniu otrzymasz przejrzysty raport z wykresami — a każda sesja
zapisywana jest dodatkowo jako **samodzielny plik HTML**, który otworzysz w dowolnej przeglądarce, także
offline. Zawiera pełny dziennik próbek wraz z tym samym podsumowaniem i wykresami.

Bez Qt i bez dołączanego Chromium: interfejs to zwykły HTML/CSS/JS renderowany przez systemowe
środowisko uruchomieniowe **Edge WebView2**. Silnik wykresów i generator raportu są współdzielone
w niezmienionej postaci między aplikacją a eksportowanymi plikami.

### Funkcje

- **Dwujęzyczność** — polski / angielski, przełączane w trakcie działania; eksportowany raport ma własny przełącznik
- **Dowolny proces** — lista z wyszukiwarką albo ręcznie wpisany PID
- **Grupy procesów** — zmierz Firefoksa, Chrome'a czy VS Code jako całość: wszystkie procesy o tej samej nazwie, całe drzewo procesu albo ręcznie zaznaczony zestaw
- **Monitorowanie na żywo** — wykresy CPU (na rdzeń i całkowite) oraz RAM z licznikiem czasu
- **Interaktywne wykresy** — autorskie wykresy SVG z celownikiem i dymkiem, dopasowane do motywu
- **Dopracowany raport** — kafelki podsumowania (min / śr / maks) i wykresy po zatrzymaniu
- **Udział procesów** — przy grupie raport pokazuje, który proces ile zużywał i za jaką część obciążenia odpowiadał
- **Eksport HTML** — każda sesja trafia do `logs/` jako samodzielny plik `.html`: pełny dziennik **+** podsumowanie **+** wykresy, obsługa trybu jasnego i ciemnego, działa offline
- **Zero zależności webowych** — wszystko jest wbudowane w plik; nic nie jest pobierane w trakcie działania

### Wymagania

| Zależność | Wersja    |
|-----------|-----------|
| Python    | 3.11+     |
| pywebview | najnowsza |
| psutil    | najnowsza |

> W systemie Windows pywebview korzysta ze środowiska **Edge WebView2**, preinstalowanego w Windows 10/11.

### Szybki start

```bash
git clone https://github.com/MowMiMazur/UsageMonitor.git
cd UsageMonitor
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

1. Kliknij **Wybierz program** i wskaż proces (albo wpisz PID).
2. Wybierz **zakres**: jeden proces, wszystkie o tej samej nazwie, proces z potomkami albo ręcznie zaznaczone.
3. Kliknij **Rozpocznij monitoring** — pojawią się wykresy na żywo i licznik czasu.
4. Kliknij **Zatrzymaj monitoring** — wyświetli się raport.
5. Otwórz eksportowany **raport HTML** z poziomu aplikacji albo znajdź go w katalogu `logs/`.

### Struktura projektu

```
UsageMonitor/
├── main.py               # Punkt wejścia — tworzy okno pywebview
├── requirements.txt
├── version.txt           # Metadane wersji dla PyInstallera
├── build.ps1             # Skrypt budowania dla Windows (jedna komenda)
├── assets/               # Ikona aplikacji
├── core/
│   ├── api.py            # Most JS <-> Python (js_api)
│   ├── monitor.py        # Pętla próbkowania (wątek w tle, bez zależności GUI)
│   ├── report.py         # Buduje samodzielny raport HTML
│   ├── group.py          # Rozwiązywanie grupy procesów (nazwa / drzewo / zestaw)
│   ├── updates.py        # Sprawdzanie nowej wersji (API maznet.pl, cache + ETag)
│   ├── constants.py
│   └── utils.py          # Ścieżki zasobów, katalog danych i lista procesów
└── web/                  # Cały interfejs użytkownika
    ├── index.html        # Powłoka aplikacji (jedna strona)
    ├── css/
    │   ├── theme.css     # Wspólny system projektowy (aplikacja + raport)
    │   └── app.css       # Style powłoki aplikacji
    └── js/
        ├── i18n.js       # Wspólny słownik PL/EN (aplikacja + raport)
        ├── charts.js     # Wspólny silnik wykresów SVG
        ├── report.js     # Wspólny generator raportu i podsumowania
        ├── updates.js    # Modal i plakietka informujące o aktualizacji
        └── app.js        # Logika powłoki aplikacji
```

Pliki `web/js/charts.js`, `web/js/report.js` i `web/js/i18n.js` są współdzielone: ten sam kod rysuje
wykresy, buduje podsumowania i tłumaczy interfejs w aplikacji, w raporcie w oknie programu oraz
w każdym eksportowanym pliku HTML.

### Monitorowanie grup procesów

Nowoczesne przeglądarki i edytory działają jako kilkanaście procesów, więc pomiar jednego PID-u mówi
niewiele. Poza trybem pojedynczego procesu UsageMonitor obsługuje trzy zakresy grupowe:

| Zakres | Co obejmuje |
|---|---|
| **Ta sama nazwa** | wszystkie procesy o nazwie wskazanego procesu (np. każdy `firefox.exe`) |
| **Z potomkami** | wskazany proces oraz całe jego drzewo procesów potomnych |
| **Zaznaczone** | dowolny zestaw PID-ów zaznaczony ręcznie na liście |

Skład grupy w trybach „ta sama nazwa" i „z potomkami" jest ustalany na nowo przy każdej próbce, więc
procesy otwierane i zamykane w trakcie sesji (nowe karty przeglądarki) są uwzględniane. Tryb
„z potomkami" zatrzymuje też procesy, których rodzic już zakończył działanie — Windows przypisuje
sieroty do innego rodzica, a ich pominięcie po cichu zaniżałoby pomiar. Sesja kończy się sama, gdy
zniknie ostatni proces z grupy.

Wykresy pokazują sumę dla całej grupy, plus dodatkowy wykres liczby procesów w czasie. Pod nimi
znajduje się tabela z rozbiciem na poszczególne procesy: średnie i maksymalne zużycie oraz udział
w łącznym obciążeniu CPU.

> **Uwaga o pamięci:** RAM grupy to suma RSS jej procesów. Procesy jednej aplikacji współdzielą
> biblioteki i pamięć, więc ta sama pamięć bywa policzona wielokrotnie i wynik jest zawyżony.
> Raport zaznacza to przy wykresie RAM.

### Sprawdzanie aktualizacji

Po starcie aplikacja pyta publiczne API `https://maznet.pl/api/v1/updates/usagemonitor` o najnowszą
wersję. Zapytanie idzie w osobnym wątku, bez tokenów i bez ciasteczek; odpowiedź trafia do cache
(`%LOCALAPPDATA%\UsageMonitor\update-cache.json`) razem z nagłówkiem `ETag`, więc kolejne sprawdzenia
kończą się kodem 304. Sieć jest odpytywana najwyżej raz na godzinę, a limit 429 jest respektowany.
Gdy dostępna jest nowsza wersja, pojawia się modal oraz plakietka przy numerze wersji w stopce; brak
sieci lub błąd API nie pokazuje niczego.

### Budowanie pliku wykonywalnego

```powershell
.\build.ps1
```

Skrypt sam wykrywa Pythona, pyta o numer wersji, instaluje zależności oraz PyInstallera, kompiluje
jednoplikowy program dla Windows (dołączając katalog `web/` i backend pywebview) i zapisuje wynik do
`exec/UsageMonitor-{wersja}.exe`.

> Jeśli PowerShell blokuje uruchamianie skryptów, wykonaj jednorazowo:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Licencja

Projekt udostępniany na **Licencji Apache 2.0** — możesz go swobodnie używać, modyfikować
i rozpowszechniać, również w projektach komercyjnych. W zamian musisz **zachować informację
o autorstwie**: pozostawić noty o prawach autorskich i autorstwie, dołączyć plik [NOTICE](NOTICE)
(wskazujący Mateusza Mazura / MAZNET jako autora) do każdej kopii lub pracy pochodnej oraz oznaczyć
wprowadzone przez siebie zmiany. Szczegóły w pliku [LICENSE](LICENSE).

### Autor

**Mateusz Mazur** (MAZNET) · [maznet.pl](https://maznet.pl)

<div align="right"><a href="#top">↑ do góry</a></div>

---

## English

A small Python core with a fully web-based (HTML/CSS/JS) interface rendered in a native window.

### Overview

Point UsageMonitor at a running process (by PID or picked from a list) and watch its CPU and RAM usage
live. When you stop, you get a clean report with charts — and every session is also saved as a
**self-contained HTML file** you can open in any browser, offline, showing the full sample log together
with the same summary and charts.

No Qt, no bundled Chromium: the UI is plain HTML/CSS/JS rendered through the OS **Edge WebView2** runtime.
The chart engine and report renderer are shared verbatim between the live app and the exported files.

### Features

- **Bilingual** — Polish / English, switchable at runtime; the exported report ships with its own toggle
- **Pick any process** — searchable list, or type a PID directly
- **Process groups** — measure Firefox, Chrome or VS Code as a whole: every process sharing a name, a full process tree, or a hand-picked set
- **Live monitoring** — real-time CPU (per-core & total) and RAM charts with an elapsed timer
- **Interactive charts** — custom SVG line charts with crosshair + tooltip, theme-aware
- **Polished report** — summary tiles (min / avg / max) and charts on stop
- **Per-process share** — for a group, the report shows which process used what and how much of the load it accounted for
- **HTML export** — each session saved to `logs/` as a standalone `.html`: full log **+** summary **+** charts, light/dark aware, works offline
- **Zero web dependencies** — everything is inlined; nothing is fetched at runtime

### Requirements

| Dependency | Version |
|------------|---------|
| Python     | 3.11+   |
| pywebview  | latest  |
| psutil     | latest  |

> On Windows, pywebview uses the **Edge WebView2** runtime, preinstalled on Windows 10/11.

### Getting started

```bash
git clone https://github.com/MowMiMazur/UsageMonitor.git
cd UsageMonitor
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

1. Click **Pick a program** and choose a process (or type a PID).
2. Pick a **scope**: one process, every process with that name, a process and its descendants, or a hand-picked set.
3. Click **Start monitoring** — live charts and a timer appear.
4. Click **Stop monitoring** — the report is shown.
5. Open the exported **HTML report** from the app, or find it in `logs/`.

### Project structure

```
UsageMonitor/
├── main.py               # Entry point — creates the pywebview window
├── requirements.txt
├── version.txt           # PyInstaller version metadata
├── build.ps1             # One-command Windows build script
├── assets/               # App icon
├── core/
│   ├── api.py            # JS <-> Python bridge (js_api)
│   ├── monitor.py        # Sampling loop (background thread, no GUI deps)
│   ├── report.py         # Builds the self-contained HTML report
│   ├── group.py          # Process-group resolution (name / tree / set)
│   ├── updates.py        # Version check (maznet.pl API, cache + ETag)
│   ├── constants.py
│   └── utils.py          # Resource paths, data dir & process list
└── web/                  # The entire user interface
    ├── index.html        # App shell (single page)
    ├── css/
    │   ├── theme.css     # Shared design system (app + report)
    │   └── app.css       # App-shell styles
    └── js/
        ├── i18n.js       # Shared PL/EN dictionary (app + report)
        ├── charts.js     # Shared SVG chart engine
        ├── report.js     # Shared report/summary renderer
        ├── updates.js    # Update modal & footer badge
        └── app.js        # App-shell logic
```

`web/js/charts.js`, `web/js/report.js` and `web/js/i18n.js` are shared: the same code renders charts,
summaries and translations in the live app, in the in-app report, and inside every exported HTML file.

### Process-group monitoring

Modern browsers and editors run as a dozen processes, so measuring a single PID tells you little.
Beside the single-process mode, UsageMonitor supports three group scopes:

| Scope | What it covers |
|---|---|
| **Same name** | every process sharing the picked process's name (e.g. each `firefox.exe`) |
| **With children** | the picked process plus its entire descendant tree |
| **Selected** | any set of PIDs ticked by hand in the list |

In "same name" and "with children" the membership is re-resolved on every sample, so processes that
open and close mid-session (new browser tabs) are counted. "With children" also keeps members whose
parent has already exited — Windows reparents orphans, and dropping them would silently understate the
measurement. The session ends by itself once the last member is gone.

The charts show the group total, plus an extra chart tracking the process count over time. Below them
a table breaks the session down per process: average and peak usage, and each one's share of the
group's total CPU load.

> **A note on memory:** group RAM is the sum of its members' RSS. Processes of one application share
> libraries and memory, so the same pages get counted more than once and the figure runs high. The
> report flags this next to the RAM chart.

### Update check

On start-up the app asks the public API `https://maznet.pl/api/v1/updates/usagemonitor` for the latest
version. The request runs on its own thread, with no tokens and no cookies; the response is cached
(`%LOCALAPPDATA%\UsageMonitor\update-cache.json`) together with its `ETag`, so follow-up checks end in
a 304. The network is polled at most once an hour and a 429 back-off is honoured. When a newer
version exists, a modal appears along with a badge next to the version number in the footer; an
offline machine or an API error shows nothing.

### Building an executable

```powershell
.\build.ps1
```

Auto-detects Python, asks for a version, installs dependencies + PyInstaller, compiles a single-file
Windows executable (bundling `web/` and the pywebview backend), and writes it to
`exec/UsageMonitor-{version}.exe`.

> If PowerShell blocks script execution, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### License

Released under the **Apache License 2.0** — free to use, modify, and distribute, including in commercial
projects. In return you must **preserve attribution**: keep the copyright and authorship notices and
include the [NOTICE](NOTICE) file (crediting Mateusz Mazur / MAZNET as the author) with any copy or
derivative work, and state any changes you make. See [LICENSE](LICENSE).

### Author

**Mateusz Mazur** (MAZNET) · [maznet.pl](https://maznet.pl)

<div align="right"><a href="#top">↑ back to top</a></div>
