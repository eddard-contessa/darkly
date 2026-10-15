#!/usr/bin/env python3
"""
Darkly -- Guess (hidden file) -- obhod labirinta /.hidden/ (versiya 3)

Chto izmenilos':
  Ves' podrobnyy vyvod (progress, anomalii, itog) teper' pishetsya v
  tekstovyy fayl "darkly_hidden_results.txt" ryadom so skriptom,
  a ne v konsol'. V konsoli budet tol'ko odna nachal'naya stroka i
  odna finalnaya, chtoby bylo ponyatno, chto skript zapushchen i
  kogda on zakonchil.

  Fayl otkryvaetsya v kodirovke UTF-8, poetomu frantsuzskiy tekst
  (à i t.p.) sohranitsya korrektno, dazhe esli konsol' Windows
  ne umeet ego pokazyvat'.

Kak zapustit' (Windows):
  pip install requests
  python darkly_hidden_crawler.py

Posle zaversheniya otkroy fayl darkly_hidden_results.txt (naprimer,
v Bloknote ili v VS Code) -- tam budet ves' log i, esli povezyot,
naydennaya anomaliya.
"""

import re
import sys
import threading
import requests
import concurrent.futures as cf

BASE_URL = "http://127.0.0.1:8080/.hidden/"
NUM_WORKERS = 50
PROGRESS_EVERY = 200
OUTPUT_FILE = "darkly_hidden_results.txt"

KNOWN_TROLL_TEXT = "Demande à ton voisin de droite"

LINK_RE = re.compile(r'<a href="([^"]+)">[^<]+</a>')

session = requests.Session()

log_lock = threading.Lock()
log_file = open(OUTPUT_FILE, "w", encoding="utf-8")


def log(msg):
    """Pishet stroku v fayl (potokobezopasno) i srazu sbrasyvaet na disk."""
    with log_lock:
        log_file.write(msg + "\n")
        log_file.flush()


processed_dirs = 0
processed_files = 0
counters_lock = threading.Lock()

anomalies = []

executor = cf.ThreadPoolExecutor(max_workers=NUM_WORKERS)
futures_lock = threading.Lock()
pending_futures = []


def submit(fn, *args):
    with futures_lock:
        fut = executor.submit(fn, *args)
        pending_futures.append(fut)


def bump_progress(kind):
    global processed_dirs, processed_files
    with counters_lock:
        if kind == "dir":
            processed_dirs += 1
        else:
            processed_files += 1
        total = processed_dirs + processed_files
        if total % PROGRESS_EVERY == 0:
            log(f"... obrabotano: papok={processed_dirs} faylov={processed_files}")


def process_dir(url):
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        log(f"[oshibka papki] {url}: {e}")
        bump_progress("dir")
        return

    for href in LINK_RE.findall(resp.text):
        if href in ("../", "./"):
            continue
        full_url = url + href
        if href.endswith("/"):
            submit(process_dir, full_url)
        else:
            submit(process_file, full_url)

    bump_progress("dir")


def process_file(url):
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        content = resp.text
    except Exception as e:
        log(f"[oshibka fayla] {url}: {e}")
        bump_progress("file")
        return

    normalized = content.strip()
    if normalized != KNOWN_TROLL_TEXT.strip():
        log(f"\n[!] ANOMALIYA NAYDENA: {url}")
        log(f"    soderzhimoe (do 300 simvolov): {content[:300]!r}\n")
        anomalies.append((url, content))

    bump_progress("file")


def main():
    print(f"Zapushcheno. Ves' log pishetsya v fayl: {OUTPUT_FILE}")
    print("Otkroy etot fayl v Bloknote / VS Code, chtoby sledit' za progressom.")
    sys.stdout.flush()

    log(f"Nachinayu polnost'yu parallel'nyy obhod {BASE_URL} ...")
    log(f"Potokov: {NUM_WORKERS}. Progress kazhdye {PROGRESS_EVERY} obrabotannyh elementov.\n")

    submit(process_dir, BASE_URL)

    while True:
        with futures_lock:
            not_done = [f for f in pending_futures if not f.done()]
        if not not_done:
            break
        cf.wait(not_done, timeout=1)

    executor.shutdown(wait=True)

    log("\n" + "=" * 60)
    log(f"Vsego obrabotano papok: {processed_dirs}, faylov: {processed_files}")
    if anomalies:
        log(f"Naydeno anomaliy: {len(anomalies)}")
        for url, content in anomalies:
            log(f" - {url}")
            log(f"   soderzhimoe: {content!r}")
    else:
        log("Nichego neobychnogo ne naydeno -- vse fayly soderzhat odin i tot zhe tekst.")

    log_file.close()
    print(f"\nGotovo! Rezul'tat polnost'yu v fayle: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nPrervano pol'zovatelem.")
        log_file.close()
        print("\nPrervano. Chastichnyy rezul'tat sohranyon v fayle.")
        sys.exit(1)
