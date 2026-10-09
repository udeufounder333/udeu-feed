# -*- coding: utf-8 -*-
"""Генератор листингов Údeu (v1 — товары stars-parts, v2 — товары AGS).

Запуск из корня репозитория:  python udeu/generate.py [--only toyota,ford] [--out .]
Читает:   feed-starsparts-<brand>.yml, feed-ags-bmw.yml (исходные фиды в корне репозитория)
Пишет:    udeu-v1-<brand>.yml, udeu-v2-bmw.yml и udeu/image_map.csv (старый путь фото -> новый)
Только стандартная библиотека Python 3.
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from brands import BRANDS, parse_category, ru_display  # noqa: E402
from parts import TYPES, INTERIOR_RX  # noqa: E402

RAW_BASE = 'https://raw.githubusercontent.com/udeufounder333/udeu-feed/main/'
IMG_DIR = 'images_udeu'

CITIES = ('Астана, Алматы, Шымкент, Караганда, Актобе, Тараз, Павлодар, Усть-Каменогорск, Семей, Атырау, '
          'Костанай, Кызылорда, Уральск, Петропавловск, Актау, Туркестан, Кокшетау, Талдыкорган, Темиртау, '
          'Экибастуз, Рудный, Жезказган, Конаев и другие города')
PAYMENT = 'Kaspi Pay, удалённый счёт, перевод, перечисление на расчётный счёт для ИП и компаний.'
PAYMENT_SHORT = 'Kaspi Pay, удалённый счёт, перевод или перечисление на расчётный счёт.'
RETURN = ('Товар надлежащего качества принимаем на реализацию: выставляем его на продажу в нашем магазине '
          'и возвращаем деньги после продажи.')
DELIVERY = f'{CITIES}. Срок 2–15 дней в зависимости от наличия.'

VENDOR_BLACKLIST = {'gz highfly ltd', 'gz highfly ltd.', 'yhimport', 'корея', 'тайвань', 'китай', 'china',
                    'udeu', 'ags', 'ags tuning', 'agstuning', 'stars-parts', 'starsparts', 'стандарт', 'реплика'}
CAR_BRAND_WORDS = {'toyota', 'lexus', 'ford', 'mercedes', 'mercedes-benz', 'bmw', 'kia', 'hyundai', 'mobis',
                   'mazda', 'nissan', 'honda', 'subaru', 'mitsubishi', 'gm', 'mopar', 'audi', 'porsche', 'volkswagen',
                   'vw', 'skoda', 'land rover', 'jaguar', 'volvo', 'bentley', 'lamborghini', 'geely', 'chery',
                   'haval', 'cadillac', 'chevrolet', 'jeep', 'dodge', 'infiniti', 'genesis', 'renault', 'opel',
                   'peugeot', 'mini', 'tesla', 'suzuki', 'isuzu', 'tank', 'great wall', 'byd', 'changan', 'exeed',
                   'jetour', 'zeekr', 'lincoln', 'gmc', 'hummer', 'chrysler'}

MAT_RULES = [
    (r'под\s+карбон|имитаци\w*\s+карбон|карбонов\w*\s+(узор|вид|рисун|текстур)|вид\s+карбон|\(карбон\s+черн', 'пластик под карбон'),
    (r'кован\w*\s+карбон', 'кованый карбон'),
    (r'карбон|carbon', 'карбон'),
    (r'нержав|нерж\.', 'нержавеющая сталь'),
    (r'алюмин', 'алюминий'),
    (r'(^|\s)стал(ь|ьн)|стальн', 'сталь'),
    (r'полиуретан', 'полиуретан'),
    (r'(^|\s)резин', 'резина'),
    (r'велюр', 'велюр'),
    (r'текстил|ворсов', 'текстиль'),
    (r'алькантар', 'алькантара'),
    (r'натуральн\w*\s+кож|кожан|(^|\s)кожа(\s|,|$)|экокож', 'кожа'),
    (r'\babs\b', 'ABS-пластик'),
    (r'стеклопластик|стекловолок', 'стеклопластик'),
    (r'полипропилен', 'полипропилен'),
    (r'пластик', 'пластик'),
]
MAT_KEY = {'алюминий': 'alu', 'сталь': 'steel', 'нержавеющая сталь': 'stainless', 'карбон': 'carbon',
           'кованый карбон': 'carbon', 'пластик под карбон': 'undercarbon', 'полиуретан': 'pu', 'резина': 'rubber',
           'велюр': 'velour', 'текстиль': 'velour'}
MAT_BENEFIT = {'алюминий': 'Алюминий лёгкий и не ржавеет.',
               'нержавеющая сталь': 'Нержавеющая сталь не ржавеет и не теряет вид.',
               'сталь': 'Сталь хорошо держит удары.',
               'карбон': 'Настоящий карбон: лёгкий, прочный и смотрится дорого.',
               'кованый карбон': 'Кованый карбон: лёгкий, прочный, с необычным рисунком.',
               'пластик под карбон': 'Пластик с рисунком под карбон: вид карбона по доступной цене.',
               'полиуретан': 'Полиуретан не впитывает воду и легко моется.',
               'резина': 'Резина держит воду и грязь, легко моется.',
               'кожа': 'Кожаная отделка смотрится дорого и служит долго.',
               'алькантара': 'Алькантара приятна на ощупь и не скользит.'}
MAT_QUERY = {'алюминий': 'алюминий', 'нержавеющая сталь': 'нержавейка', 'сталь': 'сталь', 'карбон': 'карбон',
             'кованый карбон': 'кованый карбон', 'пластик под карбон': 'под карбон', 'полиуретан': 'полиуретан',
             'резина': 'резина', 'велюр': 'велюр', 'текстиль': 'текстиль', 'кожа': 'кожа', 'алькантара': 'алькантара'}
COLOR_RULES = [
    (r'глянцев\w*\s+черн|черн\w*\s+глян', 'глянцевый черный'), (r'матов\w*\s+черн|черн\w*\s+мат', 'матовый черный'),
    (r'матов\w*\s+хром', 'матовый хром'), (r'черн\w*\s+хром', 'черный хром'), (r'красн\w*\s+карбон', 'красный карбон'),
    (r'(^|\s)черн', 'черный'), (r'(^|\s)бел(ый|ая|ое|ые)', 'белый'), (r'серебр', 'серебристый'),
    (r'(^|\s)сер(ый|ая|ое|ые)(\s|,|$)', 'серый'), (r'красн', 'красный'), (r'(^|\s)син(ий|яя|ее|ие)', 'синий'),
    (r'бронз', 'бронза'), (r'золот', 'золотой'), (r'бежев', 'бежевый'), (r'коричнев', 'коричневый'),
    (r'(^|\s)хром', 'хром'), (r'антрацит', 'антрацит'), (r'графит|оружейн', 'графит'), (r'дымчат|тонирован', 'дымчатый'),
    (r'прозрачн', 'прозрачный'), (r'(^|\s)зел[её]н', 'зелёный'), (r'оранжев', 'оранжевый'), (r'ж[её]лт', 'жёлтый'),
]
NOT_BRAND_WORDS = {'оригинал', 'реплика', 'комплект', 'компл', 'набор', 'шт', 'уп', 'пара', 'седан', 'хэтчбек',
                   'универсал', 'купе', 'кроссовер', 'внедорожник', 'рестайлинг', 'дорест', 'диз', 'бенз', 'at', 'mt',
                   'лев', 'прав', 'левый', 'правый', 'китай', 'тайвань', 'корея', 'передние', 'задние', 'передний',
                   'задний', 'левая', 'правая', 'черный', 'черная', 'белый', 'хром', 'под покраску', 'тип2', 'тип 2'}
GROUP_SKIP = {'Аксессуары', 'Сувениры и аксессуары', 'Автохимия и уход'}

GENDER = {
    'm': dict(rassch='рассчитан', podoydet='подойдёт', krep='крепится', sdelan='сделан', budet='будет',
              potuskneet='потускнеет', pron='он'),
    'f': dict(rassch='рассчитана', podoydet='подойдёт', krep='крепится', sdelan='сделана', budet='будет',
              potuskneet='потускнеет', pron='она'),
    'n': dict(rassch='рассчитано', podoydet='подойдёт', krep='крепится', sdelan='сделано', budet='будет',
              potuskneet='потускнеет', pron='оно'),
    'pl': dict(rassch='рассчитаны', podoydet='подойдут', krep='крепятся', sdelan='сделаны', budet='будут',
               potuskneet='потускнеют', pron='они'),
}
CARBON_ADJ = {'m': 'карбоновый', 'f': 'карбоновая', 'n': 'карбоновое', 'pl': 'карбоновые'}
TUNING_KEYS = {'bodykit', 'lip', 'diffuser', 'spoiler', 'panels', 'mirrors', 'grille', 'flares', 'steering', 'paddles', 'trim'}
NO_PREFIX_ALIASES = ('гелик', 'гелендваген', 'поер', 'эвок', 'велар', 'урус', 'юкон', 'сиерра', 'дастер', 'джолион',
                     'макан', 'рендж', 'дефендер', 'дискавери', 'фрилендер', 'эскалейд')

TRANSLIT = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                    ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
                     'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu', 'ya']))


# ---------------------------------------------------------------- helpers

def norm_ws(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    s = re.sub(r'(\d{4})\s+-\s*(?=\s|$|,)', r'\1-', s)
    return s


def esc_txt(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def split_top_level(name):
    parts, buf, depth = [], [], 0
    n = len(name)
    for i, c in enumerate(name):
        if c in '([':
            depth += 1
            buf.append(c)
        elif c in ')]':
            depth = max(0, depth - 1)
            buf.append(c)
        elif c == ',' and depth == 0:
            if i > 0 and name[i - 1].isdigit() and i + 1 < n and name[i + 1].isdigit():
                buf.append(c)
            else:
                parts.append(''.join(buf))
                buf = []
        else:
            buf.append(c)
    parts.append(''.join(buf))
    return [p.strip() for p in parts if p.strip()]


HOMO = str.maketrans({'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'y': 'у', 'A': 'А', 'C': 'С',
                      'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'K': 'К', 'M': 'М', 'H': 'Н', 'T': 'Т', 'B': 'В'})


HOMO_BACK = str.maketrans({v: k for k, v in {'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'y': 'у',
                                                  'A': 'А', 'C': 'С', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'K': 'К',
                                                  'M': 'М', 'H': 'Н', 'T': 'Т', 'B': 'В'}.items()})


def fix_mixed(word):
    """«Диcк» с латинской c -> «Диск», «LЕD» с кириллической Е -> «LED»."""
    if re.search(r'[а-яё]', word, re.I) and re.search(r'[a-z]', word, re.I):
        cyr = len(re.findall(r'[а-яё]', word, re.I))
        lat = len(re.findall(r'[a-z]', word, re.I))
        if cyr > lat:
            return word.translate(HOMO)
        if lat > cyr:
            return word.translate(HOMO_BACK)
    return word


def clean_title(name):
    name = norm_ws(name)
    name = re.sub(r'[A-Za-zА-Яа-яЁё]+', lambda m: fix_mixed(m.group(0)), name)
    segs = split_top_level(name)
    out = []
    for s in segs:
        s = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', s)          # "Carlight Carlight" -> "Carlight"
        if out and s.lower() == out[-1].lower():
            continue
        out.append(s)
    return ', '.join(out)


def translit(s):
    s = s.lower()
    out = []
    for ch in s:
        out.append(TRANSLIT.get(ch, ch))
    s = ''.join(out)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    if len(s) > 80:
        s = s[:80].rsplit('-', 1)[0]
    return s or 'tovar'


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def accusative(phrase):
    """«защита картера» -> «защиту картера», «светодиодная балка» -> «светодиодную балку»."""
    words = phrase.split()
    out, i = [], 0
    while i < len(words) and words[i].lower() in ('хром', 'led', 'карбон', '3d', 'rgb'):
        out.append(words[i])
        i += 1
    while i < len(words) and re.search(r'(ая|яя)$', words[i].lower()):
        w = words[i]
        out.append(w[:-2] + ('ую' if w.lower().endswith('ая') else 'юю'))
        i += 1
    if i < len(words):
        w, lw = words[i], words[i].lower()
        if re.search(r'[^иь]а$', lw):
            out.append(w[:-1] + 'у')
        elif lw.endswith('я'):
            out.append(w[:-1] + 'ю')
        else:
            out.append(w)
        i += 1
    out.extend(words[i:])
    return ' '.join(out)


# ---------------------------------------------------------------- source parsing

def parse_source_description(desc, name):
    """Возвращает (предложения-описание, факты). Понимает и сырой формат stars-parts, и прошлый HTML (Toyota/Jaguar)."""
    facts = {}
    desc = desc or ''
    if desc.lstrip().startswith('<p>'):
        paras = re.findall(r'<p>(.*?)</p>', desc, re.S)
        body = ''
        if len(paras) > 1 and not paras[1].startswith('<strong>'):
            body = re.sub(r'<[^>]+>', '', paras[1])
        for li in re.findall(r'<li>(.*?)</li>', desc):
            k, _, v = li.partition(':')
            k, v = k.strip(), v.strip()
            if k.startswith('Оригинальный номер'):
                facts['art'] = v
            elif k == 'Материал':
                facts['mat_txt'] = v
            elif k == 'Цвет':
                facts['color_txt'] = v
            elif k == 'Производитель':
                facts['vendor_src'] = v
        raw = body
    else:
        raw = desc
        m = re.search(re.escape(norm_ws(name)) + r'\s+—\s+([^.]+?)\.(\s|$)', norm_ws(desc))
        if m:
            facts['dash'] = m.group(1).strip()
        raw = norm_ws(raw)
        if m:
            raw = norm_ws(raw).replace(m.group(0).strip(), ' ')
    raw = re.sub(r'Доступен под заказ[^.]*\.?', ' ', raw)
    raw = re.sub(r'(Цена и заказ )?с доставкой по России\.?', ' ', raw, flags=re.I)
    raw = re.sub(r'\bпо России\b', '', raw, flags=re.I)
    raw = re.sub(r'GZ HighFly LTD\.?|YHIMPORT', '', raw, flags=re.I)
    raw = re.sub(r'Udeu предлагает:.*', '', raw, flags=re.S)        # старый шаблон AGS — фактов в нём нет
    raw = re.sub(r'Посмотреть на схеме\.*', ' ', raw)
    raw = re.sub(r'\(\s*[—-]?\s*\)', ' ', raw)
    raw = re.sub(r'(?<!\.)\.\.(?!\.)', '. ', raw)
    m = re.search(r'Оригинальн\w*\s+номер\w*(\s+детали)?\s*:?\s*([A-Za-z0-9][A-Za-z0-9\-./ ]{2,40}?)\s*(?=\.\s|\.$|$|Доступ)', raw)
    if m:
        facts.setdefault('art', m.group(2).strip().rstrip('.'))
        raw = raw[:m.start()] + ' ' + raw[m.end():]
    raw = norm_ws(raw)
    sents = []
    for s in re.split(r'(?<=[.!])\s+', raw):
        s = s.strip()
        if not s:
            continue
        ms = re.match(r'Материал\s+(.+?)\.?$', s)
        if ms:
            facts.setdefault('mat_txt', ms.group(1))
            continue
        ms = re.match(r'Цвет\s+(.+?)\.?$', s)
        if ms:
            facts.setdefault('color_txt', ms.group(1))
            continue
        ms = re.match(r'Диаметр\s+(.+?)\.?$', s)
        if ms:
            facts['diam'] = ms.group(1)
            continue
        ms = re.match(r'(Комплект|В комплекте)\s*:?\s*(.+?)\.?$', s)
        if ms and ms.group(1) == 'Комплект' and re.match(r'[а-яё]+(ей|ов|ок|ек|ых|их|ий)\b', ms.group(2)):
            ms = None
        if ms:
            kit = ms.group(2).strip()
            mq = re.match(r'^(\d+)\s*(шт|штук)', kit)
            if mq:
                facts['qty'] = f'{mq.group(1)} шт.'
            else:
                kit = kit.strip(' ,;:')
                if kit:
                    facts['kit'] = kit
            continue
        if len(s.split()) <= 3:
            continue
        if len(s.split()) <= 6 and re.search(r'(для\s+авто(мобил\w*)?|автомобильн\w*|для\s+а/м|для\s+колес|автомобиля)\.?$', s, re.I):
            continue
        sents.append(s if s.endswith(('.', '!', '?')) else s + '.')
    return sents, facts


def detect_material(text, facts):
    src = (facts.get('mat_txt') or '').lower()
    for rx, val in MAT_RULES:
        if src and re.search(rx, src):
            return val
    low = text.lower()
    for rx, val in MAT_RULES:
        if re.search(rx, low):
            return val
    return None


def detect_color(text, facts):
    src = (facts.get('color_txt') or '').lower()
    for rx, val in COLOR_RULES:
        if src and re.search(rx, src):
            return val
    if src and len(src) < 30:
        return src
    low = text.lower()
    for rx, val in COLOR_RULES:
        if re.search(rx, low):
            return val
    return None


def detect_part_brand(name):
    parts = split_top_level(name)
    if len(parts) < 2:
        return None
    tail = parts[-1].strip()
    low = tail.lower()
    words = tail.split()
    if (tail and not any(ch.isdigit() for ch in tail) and 1 <= len(words) <= 3 and low not in NOT_BRAND_WORDS
            and tail[0].isupper() and not re.search(r'под |для |^в |цвет|ткан|кож|покрас|сталь|алюм|пластик|карбон|хром', low)
            and not re.search(r'[а-яё]', low) or low in ('ттс', 'тсс', 'автоброня', 'норпласт')):
        return tail
    return None


def is_original(text):
    low = text.lower()
    if 'реплик' in low:
        return False
    return bool(re.search(r'оригинал(?!ьн\w*\s+номер)|genuine|\boem\b', low))


# ---------------------------------------------------------------- type detection

BODYKIT_STRONG = r'обвес|body\s?kit|widebody|wide\s+body|бодикит'


TRIM_START = r'^(хром\w*\s+|декоративн\w*\s+|двухслойн\w*\s+|защитн\w*\s+|карбонов\w*\s+|черн\w*\s+|глянцев\w*\s+)?(накладк|молдинг|вставк|окантовк|рамк|облицовк)'
TRIM_ALLOWED = {'sill_plates', 'lashes', 'pedals', 'mirrors', 'handles', 'flares', 'brakes', 'paddles'}


def detect_type(name_low):
    name_low = strip_leading_codes(name_low.strip()) + ' '
    if re.match(r'^наклейк|^стикер', name_low):
        return next(t for t in TYPES if t['key'] == 'stickers'), None
    if re.match(TRIM_START, name_low):
        for t in TYPES:
            if t['key'] in TRIM_ALLOWED and re.search(t['rx'], name_low) and not (t.get('not_rx') and re.search(t['not_rx'], name_low)):
                sub = next((s for s in t.get('subs', []) if re.search(s['rx'], name_low)), None)
                return t, sub
        trim = next(t for t in TYPES if t['key'] == 'trim')
        return trim, None
    if re.search(BODYKIT_STRONG, name_low) and not re.search(r'для\s+обвес|под\s+обвес|крепеж|кронштейн', name_low):
        bk = next(t for t in TYPES if t['key'] == 'bodykit')
        sub = next((s for s in bk.get('subs', []) if re.search(s['rx'], name_low)), None)
        return bk, sub
    for t in TYPES:
        if re.search(t['rx'], name_low) and not (t.get('not_rx') and re.search(t['not_rx'], name_low)):
            sub = None
            for s in t.get('subs', []):
                if re.search(s['rx'], name_low):
                    sub = s
                    break
            return t, sub
    return TYPES[-1], None


def strip_leading_codes(core):
    words = core.split()
    i = 0
    while i < len(words) - 1 and not re.search(r'[а-яё]', words[i], re.I):
        i += 1
    if i and re.search(r'[а-яё]', ' '.join(words[i:]), re.I) and '(' not in ' '.join(words[:i]):
        return ' '.join(words[i:])
    return core


def full_phrase(name, brand_slug, cat_info):
    """Начало названия до марки/модели/«для» — так называется сама деталь. Регистр исходный."""
    core = split_top_level(name)[0] if name.strip() else name
    core = re.split(r' /(?=[^ ])| / ', core, maxsplit=1)[0]
    core = strip_leading_codes(core)
    low = core.lower()
    stops = [' для ', ' подходит', ' подходят', ' на а/м', ' на авто', ' фирменн']
    b_lat, b_ru = BRANDS['bmw' if brand_slug == 'ags-bmw' else brand_slug]
    stops += [' ' + b_lat.lower().split()[0], ' ' + b_ru.lower().split()[0]]
    model_words = [w for w in re.findall(r'[a-zа-яё0-9\-]+', cat_info['disp'].lower()) if len(w) > 1][:1]
    stops += [' ' + w for w in model_words]
    for w in ('mercedes', 'мерседес', 'range rover', 'land cruiser', 'тойота', 'lexus', 'bmw', 'бмв'):
        stops.append(' ' + w)
    cut = len(low)
    for s in stops:
        k = (' ' + low).find(s)
        if k != -1:
            cut = min(cut, max(0, k - 1))
    m = re.search(r'\s(19|20)\d\d', low)
    if m:
        cut = min(cut, m.start())
    m = re.search(r'\s[a-z]{1,3}\d{2,3}\b', low)
    if m and not re.search(r'\sr\d{2}', m.group(0)):
        cut = min(cut, m.start())
    phrase = core[:cut].strip(' ,-–(')
    phrase = re.split(r'\s*\(', phrase)[0].strip(' ,-–')
    phrase = re.sub(r'\s+(на|для|в|с|к|и|под|от|по)$', '', phrase, flags=re.I).strip()
    if len(phrase.split()) > 6:
        phrase = ' '.join(phrase.split()[:6])
    return phrase


INVARIANT = {'хром', 'led', 'карбон', 'тюнинг', '3d', 'rgb', 'abs'}


def gender_of(phrase):
    for w in phrase.lower().split():
        if w in INVARIANT or re.fullmatch(r'[a-z0-9\-]+', w):
            continue
        if re.search(r'(ые|ие)$', w):
            return 'pl'
        if re.search(r'(ая|яя)$', w):
            return 'f'
        if re.search(r'(ый|ий|ой)$', w):
            return 'm'
        if re.search(r'(ое|ее)$', w):
            return 'n'
        if re.search(r'(и|ы)$', w):
            return 'pl'
        if re.search(r'(а|я)$', w):
            return 'f'
        if re.search(r'(о|е)$', w):
            return 'n'
        return 'm'
    return 'm'


ALIAS_NO_DECLINE = {'киа', 'воя', 'санта', 'лада', 'ниссан', 'юни'}


def alias_acc(alias):
    """«на Тундра» -> «на Тундру», «на Мазда сх5» -> «на Мазду сх5»."""
    out = []
    for w in alias.split():
        lw = w.lower()
        if re.fullmatch(r'[а-яё]{3,}', lw) and lw not in ALIAS_NO_DECLINE:
            if lw.endswith('а'):
                w = w[:-1] + 'у'
            elif lw.endswith('я'):
                w = w[:-1] + 'ю'
        out.append(w)
    return ' '.join(out)


KNOWN_PART_BRANDS = ['Modellista', 'TRD', 'Rival', 'ТСС', 'Автоброня', 'Brabus', 'Hamann', 'AC Schnitzer', 'M Performance',
                     'Larte Design', 'Borla', 'Rough Country', 'WeatherTech', 'Fuel Off-Road', 'Eibach', 'H&R', 'KW',
                     'Brembo', 'Seibon', '3DDesign', 'Akrapovic', 'Lorinser', 'Keyvany', 'Renegade', 'Mansory',
                     'Startech', 'Lumma', 'Topcar', 'Alpina', 'AMG', 'Norplast', 'Autofamily', 'Thule', 'Yakima',
                     'Putco', 'AVS', 'Lund', 'Bushwacker', 'Bushwaker', 'Rugged Ridge', 'Smittybilt', 'Mopar',
                     'Vland', 'VLAND', 'FT Carlight', 'AlphaRex', 'ANZO', 'Morimoto', 'Recon', 'Magnaflow', 'Corsa',
                     'Flowmaster', 'Gibson', 'MBRP', 'Remus', 'Milltek', 'Eisenmann', 'Capristo', 'Armytrix',
                     'Bilstein', 'Fox', 'Old Man Emu', 'Ironman', 'ARB', 'Warn', 'Lock Off-Road', 'OMU 4X4',
                     'Method', 'Black Rhino', 'KMC', 'Vision Wheel', 'Moto Metal', 'Mayhem', 'Voxx', 'Mamba',
                     'Ultra Wheel', 'American Racing', 'Raceline', 'Mickey Thompson', 'Pro Comp', 'Weld Racing',
                     'Larte', 'Zacoe', 'Piecha Design', 'Prior Design', 'TopCar', 'Vorsteiner', 'Novitec', 'Techart',
                     'Rowen', 'Wald', 'Artisan', 'Hofele', 'Arden', 'Kahn', 'Urban Automotive', 'Onyx', 'Overfinch']


def find_known_brand(title):
    for b in sorted(KNOWN_PART_BRANDS, key=len, reverse=True):
        if re.search(r'(?<![A-Za-zА-Яа-я])' + re.escape(b) + r'(?![A-Za-zА-Яа-я])', title):
            return 'Bushwacker' if b == 'Bushwaker' else ('Larte Design' if b == 'Larte' else b)
    return None


# ---------------------------------------------------------------- main builder

class Listing:
    pass


def build(offer, brand_slug, cat_info, groups_for_cat, used_slugs, version):
    b_lat, b_ru = BRANDS['bmw' if brand_slug == 'ags-bmw' else brand_slug]
    src_name = offer.findtext('name') or ''
    title = clean_title(TRANSLATIONS.get(norm_ws(src_name), src_name))
    if version == 'v2' and 'bmw' not in title.lower():
        title = 'BMW ' + title
    desc_src = offer.findtext('description') or ''
    sents, facts = parse_source_description(desc_src, src_name)
    text_all = f'{title} {src_name} {desc_src}'
    low_title = title.lower()

    phrase0 = full_phrase(title, brand_slug, cat_info).lower()
    t, sub = detect_type(phrase0 + ' ') if phrase0 else (TYPES[-1], None)
    if t['key'] != 'generic' and not sub:
        sub = next((s for s in t.get('subs', []) if re.search(s['rx'], strip_leading_codes(low_title) + ' ')), None)
    if t['key'] == 'generic':
        t, sub = detect_type(low_title + ' ')
    if t['key'] == 'generic':
        t2, sub2 = detect_type(' '.join(sents).lower() + ' ')
        if t2['key'] != 'generic' and t2['key'] not in ('merch', 'chem'):
            t, sub = t2, sub2
    sub = sub or {}
    compat = sub.get('compat', t.get('compat', True))

    phrase = full_phrase(title, brand_slug, cat_info)
    short = sub.get('short') or t.get('short') or phrase.lower() or 'деталь'
    gender = sub.get('gender') or (t.get('gender') if (sub.get('short') or t.get('short')) else gender_of(short))
    G = GENDER[gender]
    syn = list(sub.get('syn') or t.get('syn') or [])
    if t['key'] in ('trim', 'sill_plates') and not syn:
        if re.match(r'накладк', short):
            syn = [re.sub(r'^накладк(а|и)', lambda m: 'молдинг' if m.group(1) == 'а' else 'молдинги', short)]
        elif re.match(r'молдинг', short):
            syn = [re.sub(r'^молдинг(и)?', lambda m: 'накладки' if m.group(1) else 'накладка', short)]

    material = detect_material(f'{title} {desc_src}', facts)
    color = detect_color(title, facts)
    original = is_original(text_all)
    art = facts.get('art')
    if not art:
        m = re.search(r'оригинал\w*\s+((?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{5,})\b', title)
        if m:
            art = m.group(1)
    art_label = 'Оригинальный номер' if original else 'Артикул производителя'

    vendor = None
    for cand in (facts.get('vendor_src'), facts.get('dash'), detect_part_brand(title), find_known_brand(title)):
        if not cand:
            continue
        c = cand.strip().rstrip('.')
        cl = c.lower()
        if cl in VENDOR_BLACKLIST or len(c) > 40:
            continue
        if cl in CAR_BRAND_WORDS and not original:
            continue
        vendor = c
        break
    if not vendor and original:
        vendor = b_lat
    if vendor and vendor.lower() in ('gm',):
        vendor = 'GM'
    led = bool(re.search(r'led|светодиод', low_title))
    size = (re.search(r'\br(\d{2})', low_title) or [None, None])[1] if re.search(r'\br\d{2}', low_title) else None
    qty = facts.get('qty')
    if not qty:
        m = re.search(r'(\d+)\s*(шт|штук|част|детал)', low_title)
        if m:
            qty = f'{m.group(1)} шт.'
    kit = facts.get('kit')

    paint = False
    if re.search(r'под\s+покраск|грунт|неокраш|в\s+цвет\s+кузова', text_all.lower()):
        paint = True
    elif t.get('paint') == 'body' and material not in ('карбон', 'кованый карбон', 'пластик под карбон', 'нержавеющая сталь',
                                                      'алюминий', 'сталь') and color not in ('хром', 'матовый хром', 'черный хром'):
        paint = True
    if t['key'] in ('trim',) and not re.search(r'под\s+покраск', text_all.lower()):
        paint = False
    interior = bool(re.search(INTERIOR_RX, low_title))
    if interior:
        paint = False

    # ---- aliases
    aliases = cat_info['ru'] or [b_ru.lower()]
    cyr_aliases = [a for a in aliases if re.search(r'[а-яё]', a)] or aliases
    a0 = aliases[0]
    a1 = aliases[1] if len(aliases) > 1 else None
    first_word = a0.split()[0]
    if first_word in b_ru.lower() or a0.startswith(NO_PREFIX_ALIASES):
        ru_par = ' / '.join(ru_display(a) for a in cyr_aliases)
    else:
        ru_par = b_ru + ' ' + ' / '.join(ru_display(a) for a in cyr_aliases)
    model_full = f'{b_lat} {cat_info["disp"]}'.strip()
    yrs = cat_info['years']
    yrs_intro = (f' {yrs} выпуска' if cat_info['open'] else f' {yrs} годов выпуска') if yrs else ''
    yrs_plain = f', {yrs}' if yrs else ''
    lat = cat_info['lat']
    lat_model = ' '.join(lat.split()[1:]) if len(lat.split()) > 1 else lat
    ru_base = re.sub(r'\s+\S*\d\S*$', '', a0).strip()
    if not ru_base.startswith(b_ru.lower().split()[0]) and not ru_base.startswith(NO_PREFIX_ALIASES):
        ru_base = f'{b_ru.lower()} {ru_base}'.strip()

    # ---- intro
    ph = phrase or short
    if compat:
        s1 = f'{cap(ph)} для {model_full} ({ru_par}){yrs_intro}.'
    else:
        s1 = f'{title}.'
    intro = [s1]
    s1_words = set(re.findall(r'[а-яёa-z0-9]+', s1.lower()))
    for s in sents:
        w = set(re.findall(r'[а-яёa-z0-9]+', s.lower()))
        if w and len(w & s1_words) / len(w) > 0.7:
            continue
        intro.append(s)
    if kit:
        intro.append(f'В комплекте: {kit}.')
    about = (t.get('about_by_sub') or {}).get(short) or (t.get('about_interior') if interior and t.get('about_interior') else t.get('about'))
    if about and len(intro) < 3:
        intro.append(about)
    intro = [re.sub(r'(?<!\.)\.\.(?!\.)', '.', x) for x in intro]

    # ---- benefits
    ben = []
    if original and art:
        ben.append(f'Оригинальная деталь {vendor or b_lat}, номер {art} можно сверить в каталоге.')
    elif original:
        ben.append(f'Оригинальная деталь {vendor or b_lat}.')
    if material and MAT_BENEFIT.get(material):
        ben.append(MAT_BENEFIT[material])
    ben.extend(t.get('benefits', []))
    if vendor and not original and vendor.lower() not in CAR_BRAND_WORDS:
        ben.append(f'Производитель: {vendor}.')
    install_ok = compat and t.get('install', True) and sub.get('install', True)
    if install_ok:
        ben.append('Покрасим в цвет кузова и установим в нашем сервисе в Астане.' if paint
                   else 'Установим в нашем сервисе в Астане.')
    seen = set()
    ben = [b for b in ben if not (b in seen or seen.add(b))][:5]

    # ---- FAQ (вариант В)
    fill = dict(short=short, Short=cap(short), model=model_full, alias=ru_display(a0), mat=material or '',
                kit=cap(kit or ''), qty=qty or '', rassch=G['rassch'], podoydet=G['podoydet'],
                Podoydet=cap(G['podoydet']), krep=G['krep'], sdelan=G['sdelan'], budet=G['budet'],
                potuskneet=G['potuskneet'], short_pron=G['pron'], short_acc=accusative(short),
                vendor=vendor or b_lat, art=art or '', size=size or '')
    conds = {'always': True, 'single': bool(re.match(r'диск\s', low_title)) and 'комплект' not in low_title,
             'original': original and bool(art), 'kit': bool(kit), 'qty': bool(qty), 'led': led,
             'alu': material == 'алюминий', 'steel': material == 'сталь', 'stainless': material == 'нержавеющая сталь',
             'carbon': material in ('карбон', 'кованый карбон'), 'undercarbon': material == 'пластик под карбон',
             'pu': material == 'полиуретан', 'rubber': material == 'резина', 'velour': material in ('велюр', 'текстиль')}
    faq = []
    alias_q = ru_display(a1 if (a1 and re.search(r'[а-яё]', a1)) else a0)
    install = t.get('install', True) and sub.get('install', True)
    if compat:
        if t['key'] == 'wheels':
            faq.append((f'{cap(G["podoydet"])} ли {short} на {alias_acc(alias_q)}?',
                        f'Диск подбирается по разболтовке и вылету. Пришлите VIN, и мы проверим посадку на вашу машину.'))
        else:
            faq.append((f'{cap(G["podoydet"])} ли {short} на {alias_acc(alias_q)}?',
                        f'{cap(short)} {G["rassch"]} на {model_full}{yrs_plain}. Пришлите VIN, и мы подтвердим посадку для вашей машины.'))
    for cond, q, a in t.get('faq', []):
        if conds.get(cond):
            try:
                faq.append((q.format(**fill), a.format(**fill)))
            except (KeyError, IndexError):
                continue
            break
    second_mentions_astana = bool(faq) and 'Астан' in faq[-1][1]
    if paint and compat and install:
        faq.append((f'Можно покрасить {accusative(short)} в цвет машины?',
                    'Да. Покрасим в цвет кузова и установим в нашем сервисе в Астане.'))
    elif compat and install and not second_mentions_astana:
        faq.append((f'Где установить {accusative(short)} на {alias_acc(ru_display(a0))}?', 'В нашем сервисе в Астане.'))
    else:
        faq.append(('Сколько ждать доставку в Алматы или другой город?',
                    '2–15 дней в зависимости от наличия. Доставляем по всему Казахстану.'))
    faq.append(('Как оплатить?', PAYMENT_SHORT))

    # ---- "Ещё для"
    more = [g for g in groups_for_cat if g not in GROUP_SKIP][:6]

    # ---- HTML
    h = [f'<p><strong>{esc_txt(title)}</strong></p>', f'<p>{esc_txt(" ".join(intro))}</p>']
    if ben:
        h.append('<p><strong>Преимущества</strong></p>')
        h.append('<ul>' + ''.join(f'<li>{esc_txt(b)}</li>' for b in ben) + '</ul>')
    if compat:
        h.append('<p><strong>Совместимость</strong></p>')
        vin = ('Пришлите VIN в чат: проверим разболтовку и вылет.' if t['key'] == 'wheels'
               else 'Пришлите VIN в чат: проверим посадку для вашей машины и комплектации.')
        h.append(f'<p>{esc_txt(model_full + yrs_plain)}. {vin}</p>')
        if install_ok:
            h.append('<p><strong>Покраска и установка</strong></p>' if paint else '<p><strong>Установка</strong></p>')
            h.append('<p>В нашем сервисе в Астане.</p>')
    h.append('<p><strong>Оплата</strong></p>')
    h.append(f'<p>{PAYMENT}</p>')
    h.append('<p><strong>Доставка по Казахстану</strong></p>')
    h.append(f'<p>{DELIVERY}</p>')
    h.append('<p><strong>Возврат</strong></p>')
    h.append(f'<p>{RETURN}</p>')
    h.append('<p><strong>Частые вопросы</strong></p>')
    for q, a in faq:
        a = re.sub(r'(?<!\.)\.\.(?!\.)', '.', a)
        h.append(f'<p><strong>{esc_txt(q)}</strong><br>{esc_txt(a)}</p>')
    if more:
        h.append(f'<p><strong>Ещё для {esc_txt(model_full)} в магазине Údeu</strong></p>')
        h.append('<ul>' + ''.join(f'<li>{esc_txt(g)}</li>' for g in more) + '</ul>')
    html = '\n'.join(h)

    # ---- keywords
    q = []
    if compat:
        q.append(f'{short} {a0}')
        if a1:
            q.append(f'{short} {a1}')
        q.append(f'{short} {lat}')
        if t['key'] in TUNING_KEYS and not interior:
            q.append(f'{short} на {lat}')
        if syn:
            q.append(f'{syn[0]} {a0}')
        pl = (phrase or '').lower()
        if pl and pl != short and len(pl.split()) <= 5:
            q.append(f'{pl} {a0}')
        if material in ('карбон', 'кованый карбон') and t['key'] in TUNING_KEYS:
            q.append(f'{CARBON_ADJ[gender]} {short} на {lat}')
            q.append(f'карбон на {lat}')
        if len(syn) > 1:
            q.append(f'{syn[1]} {lat}')
        if material and MAT_QUERY.get(material):
            a0_noyear = re.sub(r'\s+\S*\d\S*$', '', a0)
            q.append(f'{short} {a0_noyear} {MAT_QUERY[material]}')
        if vendor and vendor.lower() not in CAR_BRAND_WORDS:
            q.append(f'{short} {vendor.lower()} {lat_model}')
        if art:
            q.append(art)
        if cat_info['y1']:
            q.append(f'{short} {ru_base} {cat_info["y1"]}')
        if len(syn) > 2:
            q.append(f'{syn[2]} {a0}')
        q.append(f'{short} {a0} алматы')
        q.append(f'{short} {a0} астана')
    else:
        base = (phrase or short).lower()
        q += [f'{base} {b_lat.lower()}', f'{base} {b_ru.lower()}']
        if vendor:
            q.append(f'{base} {vendor.lower()}')
        if art:
            q.append(art)
        q += [f'{base} {b_ru.lower()} алматы', f'{base} {b_ru.lower()} астана']
    q = [re.sub(r'\{size\}', size or '', x) for x in q]
    out_q, seen = [], set()
    for x in q:
        x = re.sub(r'\([^)]*\)?', ' ', x)
        x = x.replace(',', ' ').replace('"', '').replace('(', ' ').replace(')', ' ')
        x = norm_ws(x).strip(' ,-')
        x = re.sub(r'\s+', ' ', x)
        if not x or 'r ' in x and x.endswith(' r') or len(x) > 100:
            continue
        k = x.lower()
        if k in seen:
            continue
        seen.add(k)
        out_q.append(x)
    keywords = out_q[:13]

    # ---- params
    params = []
    if compat:
        params += [('Марка автомобиля', b_lat), ('Модель автомобиля', cat_info['disp'])]
        if yrs:
            params.append(('Годы выпуска', yrs.replace('с ', 'с ').replace(' года', '')))
    params.append(('Тип детали', cap(short)))
    if material:
        params.append(('Материал', material))
    if color:
        params.append(('Цвет', color))
    if kit:
        params.append(('Комплектация', kit))
    if qty:
        params.append(('Количество', qty))
    if facts.get('diam'):
        params.append(('Диаметр трубы', facts['diam']))
    if vendor:
        params.append(('Производитель', vendor))
    if art:
        params.append((art_label, art))
    if original:
        params.append(('Оригинальность', 'Оригинал'))
    elif re.search(r'реплик', text_all.lower()):
        params.append(('Оригинальность', 'Реплика'))
    params.append(('Состояние', 'Новое'))

    # ---- pictures
    base_slug = translit(title)
    slug = base_slug
    if slug in used_slugs:
        slug = f'{base_slug}-{hashlib.sha1(offer.get("id", "").encode()).hexdigest()[:6]}'
    used_slugs.add(slug)
    pics = []
    for i, pic in enumerate(offer.findall('picture'), 1):
        old = (pic.text or '').strip()
        m = re.match(re.escape(RAW_BASE) + r'(.+)$', old)
        ext = (old.rsplit('.', 1)[-1] or 'jpg').lower()
        if ext not in ('jpg', 'jpeg', 'png', 'webp', 'gif'):
            ext = 'jpg'
        new_path = f'{IMG_DIR}/{slug}-{i}.{ext}'
        pics.append((m.group(1) if m else None, new_path, old))

    L = Listing()
    L.title, L.html, L.keywords, L.params, L.vendor, L.art, L.pics = title, html, keywords, params, vendor, art, pics
    L.type, L.short, L.group, L.compat = t['key'], short, t['group'], compat
    return L


TRANSLATIONS = {}


def load_translations():
    p = os.path.join(HERE, 'translations.json')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
        for k, v in data.items():
            TRANSLATIONS[norm_ws(k)] = v


def first_pass_groups(root, brand_slug):
    """Группы деталей по каждой модели (категории) — для блока «Ещё для …»."""
    by_cat = defaultdict(Counter)
    for o in root.iter('offer'):
        name = clean_title(TRANSLATIONS.get(norm_ws(o.findtext('name') or ''), o.findtext('name') or '')).lower()
        t, _ = detect_type(name + ' ')
        by_cat[o.findtext('categoryId')][t['group']] += 1
    return {cid: [g for g, _ in c.most_common()] for cid, c in by_cat.items()}


def process(src_path, brand_slug, version, out_dir, used_slugs, img_rows, stats, write=True):
    tree = ET.parse(src_path)
    root = tree.getroot()
    shop = root.find('shop')
    nm = shop.find('name')
    b_lat = BRANDS['bmw' if brand_slug == 'ags-bmw' else brand_slug][0]
    if nm is not None:
        nm.text = f'Údeu {version} · {b_lat}'
    comp = shop.find('company')
    if comp is not None:
        comp.text = 'Údeu'
    cats = {c.get('id'): (c.text or '').strip() for c in root.iter('category')}
    cat_info = {cid: parse_category(brand_slug, n) for cid, n in cats.items()}
    groups = first_pass_groups(root, brand_slug)
    for o in root.iter('offer'):
        cid = o.findtext('categoryId')
        ci = cat_info.get(cid) or parse_category(brand_slug, '')
        L = build(o, brand_slug, ci, groups.get(cid, []), used_slugs, version)
        o.find('name').text = L.title
        o.find('description').text = L.html
        kw = o.find('keywords')
        if kw is None:
            kw = ET.SubElement(o, 'keywords')
        kw.text = ', '.join(L.keywords)
        for pic, (old_rel, new_rel, old_url) in zip(o.findall('picture'), L.pics):
            if old_rel:
                pic.text = RAW_BASE + new_rel
                img_rows.append((old_rel, new_rel))
        for tag in ('vendor', 'vendorCode'):
            for e in o.findall(tag):
                o.remove(e)
        for e in o.findall('param'):
            o.remove(e)
        if L.vendor:
            ET.SubElement(o, 'vendor').text = L.vendor
        if L.art:
            ET.SubElement(o, 'vendorCode').text = L.art
        for k, v in L.params:
            ET.SubElement(o, 'param', name=k).text = v
        stats['types'][L.type] += 1
        stats['offers'] += 1
    slug_out = 'bmw' if brand_slug == 'ags-bmw' else brand_slug
    out = os.path.join(out_dir, f'udeu-{version}-{slug_out}.yml')
    if write:
        tree.write(out, encoding='UTF-8', xml_declaration=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='.', help='папка с исходными фидами (корень репозитория)')
    ap.add_argument('--out', default='.', help='куда писать udeu-*.yml')
    ap.add_argument('--only', default='', help='через запятую: toyota,ford,ags-bmw')
    args = ap.parse_args()
    load_translations()
    only = set(x.strip() for x in args.only.split(',') if x.strip())
    jobs = []
    for p in sorted(glob.glob(os.path.join(args.src, 'feed-starsparts-*.yml'))):
        slug = os.path.basename(p)[len('feed-starsparts-'):-4]
        if slug in BRANDS:
            jobs.append((p, slug, 'v1'))
    ags = os.path.join(args.src, 'feed-ags-bmw.yml')
    if os.path.exists(ags):
        jobs.append((ags, 'ags-bmw', 'v2'))
    # имена фото зависят от всех брендов сразу (уникальность), поэтому обрабатываем всё, а пишем только выбранное
    used_slugs, img_rows = set(), []
    stats = {'types': Counter(), 'offers': 0}
    for p, slug, ver in jobs:
        write = not only or slug in only
        out = process(p, slug, ver, args.out, used_slugs, img_rows, stats, write=write)
        if write:
            print(f'{os.path.basename(out)}: ok', flush=True)
    os.makedirs(os.path.join(args.out, 'udeu'), exist_ok=True)
    with open(os.path.join(args.out, 'udeu', 'image_map.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['old', 'new'])
        w.writerows(img_rows)
    print(f'offers: {stats["offers"]}, images: {len(img_rows)}')
    print('types:', dict(stats['types'].most_common()))


if __name__ == '__main__':
    main()
