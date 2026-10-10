# -*- coding: utf-8 -*-
"""Переименование фото в формат Údeu (запускается роботом GitHub после generate.py).

Читает udeu/image_map.csv (исходный путь фото -> новое имя) и переносит файлы; git add в роботе фиксирует переименование.
Одно исходное фото может принадлежать нескольким листингам: тогда оно переносится под имя первого,
а для остальных делается копия (git хранит одинаковые файлы один раз, места в репозитории не прибавится).
Ведёт журнал udeu/image_locations.csv (исходный путь -> где файл лежит сейчас),
поэтому повторный запуск безопасен.
"""
import csv
import os
import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

MAP = sys.argv[1] if len(sys.argv) > 1 else 'udeu/image_map.csv'
LEDGER = 'udeu/image_locations.csv'


def load_ledger():
    loc = {}
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                loc[row['original']] = row['current']
    return loc


def save_ledger(loc):
    with open(LEDGER, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['original', 'current'])
        for k in sorted(loc):
            w.writerow([k, loc[k]])


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (udeu-bot)'})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    if len(data) < 200:
        raise ValueError('пустой файл')
    return data


def download(url, dst):
    """Фото с сайта поставщика -> наш файл. Если полноразмерного нет (бывает у AGS), берём миниатюру."""
    tries = [url]
    if '/360x270/' not in url and '/assets/images/products/' in url:
        head, name = url.rsplit('/', 1)
        tries.append(head + '/360x270/' + name)
    for u in tries:
        for _ in range(3):
            try:
                data = _get(u)
                os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
                with open(dst, 'wb') as f:
                    f.write(data)
                return True
            except Exception:
                continue
    return False


def fetch_remote(pairs):
    """pairs: [(url, новое имя)] — скачивает то, чего ещё нет в репозитории."""
    todo = [(u, d) for u, d in pairs if not os.path.exists(d)]
    ok = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        for res in ex.map(lambda p: download(*p), todo):
            ok += bool(res)
    print(f'скачано с сайта поставщика: {ok} из {len(todo)} (уже было: {len(pairs) - len(todo)})')


def main():
    loc = load_ledger()
    groups = {}          # исходное фото -> список новых имён (по порядку)
    owner = {}           # новое имя -> исходное фото
    remote = []
    with open(MAP, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            orig, new = row['old'], row['new']
            if orig.startswith('http'):
                remote.append((orig, new))
                continue
            if new in owner:
                if owner[new] != orig:
                    print(f'ВНИМАНИЕ: одно имя для двух фото: {new}')
                continue
            owner[new] = orig
            groups.setdefault(orig, []).append(new)

    moved = copied = done = missing = 0
    for orig, targets in groups.items():
        primary = targets[0]
        cur = loc.get(orig, orig)
        # где сейчас лежит файл: по журналу, на старом месте или уже под одним из новых имён
        src = None
        for cand in [primary, cur, orig] + targets[1:]:
            if os.path.exists(cand):
                src = cand
                break
        if src is None:
            missing += len(targets)
            continue
        if src != primary:
            os.makedirs(os.path.dirname(primary) or '.', exist_ok=True)
            if src in targets:
                shutil.copy2(src, primary)   # файл уже нужен под своим именем — не трогаем его
            else:
                os.rename(src, primary)
            moved += 1
        else:
            done += 1
        loc[orig] = primary
        for t in targets[1:]:
            if os.path.exists(t):
                done += 1
                continue
            os.makedirs(os.path.dirname(t) or '.', exist_ok=True)
            shutil.copy2(primary, t)
            copied += 1
    if remote:
        fetch_remote(remote)
    save_ledger(loc)
    print(f'перенесено: {moved}, скопировано для общих фото: {copied}, уже на месте: {done}, не найдено: {missing}')


if __name__ == '__main__':
    main()
