# -*- coding: utf-8 -*-
"""Переименование фото в формат Údeu (запускается роботом GitHub после generate.py).

Читает udeu/image_map.csv (исходный путь фото -> новое имя) и переносит файлы; git add в роботе фиксирует переименование.
Ведёт журнал udeu/image_locations.csv (исходный путь -> где файл лежит сейчас),
поэтому повторный запуск безопасен: уже перенесённые фото не теряются, а при смене названия
листинга фото просто переезжает на новое имя.
"""
import csv
import os
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


def move_files(pairs):
    """Обычный перенос файлов (быстро даже для 80 тысяч фото). Git сам увидит переименование при git add."""
    for src, dst in pairs:
        os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
        if os.path.exists(dst):
            continue
        os.rename(src, dst)


def main():
    loc = load_ledger()
    moves, missing, done = [], 0, 0
    targets = {}
    with open(MAP, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            orig, new = row['old'], row['new']
            if new in targets and targets[new] != orig:
                print(f'ВНИМАНИЕ: одно имя для двух фото: {new}')
                continue
            targets[new] = orig
            cur = loc.get(orig, orig)
            if cur == new and os.path.exists(new):
                done += 1
                continue
            if os.path.exists(cur):
                moves.append((cur, new))
                loc[orig] = new
            elif os.path.exists(new):
                loc[orig] = new
                done += 1
            else:
                missing += 1
    if moves:
        move_files(moves)
        failed = 0
        for orig, cur in list(loc.items()):
            if not os.path.exists(cur) and os.path.exists(orig):
                loc[orig] = orig
                failed += 1
        if failed:
            print(f'не удалось перенести: {failed} (останутся на старом месте до следующего запуска)')
    save_ledger(loc)
    print(f'перенесено: {len(moves)}, уже на месте: {done}, не найдено: {missing}')


if __name__ == '__main__':
    main()
