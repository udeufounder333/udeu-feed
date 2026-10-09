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


def main():
    loc = load_ledger()
    groups = {}          # исходное фото -> список новых имён (по порядку)
    owner = {}           # новое имя -> исходное фото
    with open(MAP, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            orig, new = row['old'], row['new']
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
    save_ledger(loc)
    print(f'перенесено: {moved}, скопировано для общих фото: {copied}, уже на месте: {done}, не найдено: {missing}')


if __name__ == '__main__':
    main()
