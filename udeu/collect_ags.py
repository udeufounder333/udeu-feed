# -*- coding: utf-8 -*-
"""Сбор товаров Údeu v2 с сайта поставщика (agstuning.ru) в исходный фид feed-ags-<марка>.yml.

Запускается роботом перед generate.py. Если фид уже есть, повторно не собирает
(нужно обновить — запустить с --refresh или удалить файл). Если сайт недоступен,
оставляет старый фид и не роняет робота.

Правила отбора (утверждены пользователем для BMW, применяются так же к Mercedes):
- наклейки/стикеры — нет;
- накладки на руль — только карбон;
- тканевый подлокотник — нет;
- раздел «Интерьер» — только карбон;
- хром и нержавейка — нет;
- защитные накладки порогов — только оригинал;
- окантовка фар — только пластик или карбон;
- без цены — в фид без поля цены: на сайте «Цену уточняйте», в описании «Цена по запросу».
Цена = цена поставщика × 4.
"""
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = 'https://agstuning.ru'
PRICE_K = 4

# марка: (id марки на сайте, {адрес модели на сайте: (id категории в фиде, название группы Satu)})
CONFIG = {
    'mercedes': (66, {
        'AMG-GT-C190-R190': ('9756748', 'AMG GT C190 / R190 (2014-2021)'),
        'AMG-GT-X290': ('9756749', 'AMG GT 4-door X290 (2018-н.в.)'),
        'c117-cla-class': ('9716741', 'CLA-class C117 (2013-2019)'),
        'C118-CLA-Class-2019': ('9716742', 'CLA-class C118 (2019-н.в.)'),
        'CLE-C236-Coupe-2023': ('9716743', 'CLE-class C236/A236 (2023-н.в.)'),
        'CLS-C257-2018': ('9716745', 'CLS-class W257 (2018-н.в.)'),
        'EQB-X243': ('9756750', 'EQB X243 (2021-н.в.)'),
        'EQC-N293': ('9756751', 'EQC N293 (2019-2024)'),
        'EQE-V295': ('9716755', 'EQE-class W295 (2022-н.в.)'),
        'EQS-V297': ('9716757', 'EQS-class V297 (2022-н.в.)'),
        'GLA-2020': ('9716761', 'GLA-class H247 (2020-н.в.)'),
        'GLB-X247-2020': ('9716763', 'GLB-class X247 (2019-н.в.)'),
        'glc': ('9716764', 'GLC-class X253 / Coupe C253 (2015-2019)'),
        'GLC-X254-2022': ('9716766', 'GLC-class X254 (2022-н.в.)'),
        'GLE-Coupe-C167-2020': ('9716767', 'GLE Coupe C167 (2020-н.в.)'),
        'gle-coupe-c292': ('9716768', 'GLE Coupe C292 (2015-2019)'),
        'GLE-V167': ('9716769', 'GLE-class V167 (2020-н.в.)'),
        'GLS-X167-2020': ('9716773', 'GLS-class X167 (2020-н.в.)'),
        'R232-SL-2022': ('9716785', 'SL-Class R232 (2021-2025)'),
        'sprinter-w903': ('9756752', 'Sprinter W903 (1995-2006)'),
        'sprinter-w906': ('9756753', 'Sprinter W906 (2006-2018)'),
        'Sprinter-W907': ('9756754', 'Sprinter W907 (2018-н.в.)'),
        'v-class-2014-w447-vito': ('9756756', 'V-class / Vito W447 (2014-2023)'),
        'w164': ('9716774', 'M-class W164 (2005-2011)'),
        'w166-ml': ('9716775', 'M-class W166 (2011-2015)'),
        'w176-a-class': ('9716729', 'A-class W176 (2012-2018)'),
        'W177-A-Class-2018': ('9716730', 'A-class W177 (2019-н.в.)'),
        'w205-c-class': ('9716738', 'C-class W205 (2015-2021)'),
        'W206-C-Class-2021': ('9716739', 'C-class W206 (2022-н.в.)'),
        'w213-e-class-2016': ('9716750', 'E-class W213 (2016-2021)'),
        'W214-E-Class-2023': ('9716752', 'E-class W214 (2024-н.в.)'),
        'w218-cls': ('9716744', 'CLS-class W218 (2010-2017)'),
        'w219': ('9756755', 'CLS-class W219 (2004-2010)'),
        'w222': ('9716780', 'S-class W222 (2013-2020)'),
        'W223-S-Class-2020': ('9716781', 'S-class W223 (2021-н.в.)'),
        'w463-g-class-W465-w464': ('9716028', 'G-Class W463 (2012-2018)'),
        'W463A-W464-2018': ('9716027', 'G-class W463 Facelift (2019-2024)'),
        'x166-gl': ('9716760', 'GL-class X166 (2013-2015)'),
        'x204-glk': ('9716771', 'GLK-class X204 (2008-2015)'),
    }),
}


def post(data, as_json=False, tries=4):
    body = urllib.parse.urlencode(data).encode()
    for t in range(tries):
        try:
            req = urllib.request.Request(BASE + '/ajaxfilter.html', data=body, headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (udeu-bot)',
            })
            with urllib.request.urlopen(req, timeout=40) as r:
                txt = r.read().decode('utf-8', 'replace')
            if not as_json:
                return txt
            try:
                return json.loads(txt)
            except ValueError:
                return []
        except Exception:
            time.sleep(2 + t * 2)
    return None


def links(htm):
    out = []
    for m in re.finditer(r'<a\b[^>]*?href="([^"]*)"[^>]*?data-id="(\d+)"[^>]*>(.*?)</a>', htm or '', re.S):
        out.append((m.group(2), m.group(1), html.unescape(re.sub(r'<[^>]+>', '', m.group(3))).strip()))
    return out


def excluded(title, cat, cats):
    t = title.lower()
    if 'Наклейки, стикеры' in cats or re.search(r'наклейк|стикер', t):
        return 'наклейки'
    if re.search(r'накладк', t) and re.search(r'рул[ья]|руле', t) and 'карбон' not in t:
        return 'руль не карбон'
    if 'подлокотник' in t and 'ткан' in t:
        return 'подлокотник ткань'
    if cat == 'Интерьер' and 'карбон' not in t:
        return 'салон не карбон'
    if re.search(r'хром|нержав', t):
        return 'хром/нержавейка'
    if ('Защитные накладки' in cats or 'накладк' in t) and 'порог' in t and 'оригинал' not in t:
        return 'накладки порогов не оригинал'
    if re.search(r'окантовк|обрамлен', t) and 'фар' in t and not re.search(r'пластик|карбон', t):
        return 'окантовка фар'
    return None


def collect(brand):
    mark_id, models = CONFIG[brand]
    site_models = links(post({'do': 'getModelByMark', 'parent_id': mark_id}))
    if not site_models:
        raise RuntimeError('сайт не ответил')
    by_slug = {}
    for mid, href, name in site_models:
        by_slug[href.rstrip('/').split('/')[-1].lower()] = (mid, name)
    lower_cfg = {k.lower(): k for k in models}
    items = {}
    for slug in models:
        if slug.lower() not in by_slug:
            print(f'  нет модели на сайте: {slug}')
            continue
        mid, mname = by_slug[slug.lower()]
        cats = [(cid, n) for cid, _h, n in links(post({'do': 'getCatsByModel', 'parent_id': mid})) if cid != '0']
        raw = 0
        for cid, cname in cats:
            off = 0
            while off < 6000:
                arr = post({'do': 'getProductsByCat', 'parent_id': mid, 'filter_id': cid, 'offset': off}, as_json=True)
                if not arr:
                    break
                for p in arr:
                    raw += 1
                    it = items.get(p['uri'])
                    if not it:
                        items[p['uri']] = {'uri': p['uri'], 'title': html.unescape(p.get('pagetitle') or '').strip(),
                                           'price': p.get('price') or '0', 'thumb': p.get('thumb') or '',
                                           'slug': slug, 'cat': cname, 'cats': [cname]}
                    elif cname not in it['cats']:
                        it['cats'].append(cname)
                if len(arr) < 32:
                    break
                off += 32
        print(f'  {slug}: {len(cats)} разделов, {raw} позиций')
    # модель товара — по адресу его страницы, если это одна из наших моделей
    for it in items.values():
        m = re.search(r'katalog/[^/]+/([^/]+)/', it['uri'], re.I)
        if m and m.group(1).lower() in lower_cfg:
            it['slug'] = lower_cfg[m.group(1).lower()]
    return models, items


def write_feed(brand, models, items, path):
    stats, keep = {}, []
    for it in items.values():
        why = excluded(it['title'], it['cat'], it['cats'])
        price = int(re.sub(r'\D', '', str(it['price'])) or 0)
        stats[why or 'в фид'] = stats.get(why or 'в фид', 0) + 1
        if not why:
            keep.append((it, price))
    esc = lambda s: (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    used = sorted({models[it['slug']] for it, _ in keep}, key=lambda x: x[1])
    with open(path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<yml_catalog date="%s">\n  <shop>\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
        f.write(f'    <name>Údeu v2 · {brand}</name>\n    <categories>\n')
        for cid, name in used:
            f.write(f'      <category id="{cid}">{esc(name)}</category>\n')
        f.write('    </categories>\n    <offers>\n')
        for it, price in keep:
            oid = 'ags-' + hashlib.sha1(it['uri'].encode()).hexdigest()[:12]
            cid = models[it['slug']][0]
            pic = it['thumb'].replace('/360x270/', '/')
            if pic and not pic.startswith('http'):
                pic = BASE + '/' + pic.lstrip('/')
            f.write(f'        <offer id="{oid}" available="true">\n')
            f.write(f'          <name>{esc(it["title"])}</name>\n')
            f.write(f'          <categoryId>{cid}</categoryId>\n')
            if price > 0:
                f.write(f'          <price>{price * PRICE_K}</price>\n')
            if pic:
                f.write(f'          <picture>{esc(pic)}</picture>\n')
            f.write('          <description></description>\n')
            f.write('        </offer>\n')
        f.write('    </offers>\n  </shop>\n</yml_catalog>\n')
    print(f'  {os.path.basename(path)}: ' + ', '.join(f'{k}: {v}' for k, v in sorted(stats.items(), key=lambda x: -x[1])))


def split_multibrand(path, out_dir='.'):
    """feed-ags-china.yml (несколько марок в одном файле, у категорий атрибут brand="<slug>")
    -> feed-ags-<slug>.yml по одной марке: так их обрабатывает generate.py."""
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    shop = root.find('shop')
    cats = list(shop.find('categories'))
    brand_of = {c.get('id'): c.get('brand') for c in cats}
    by_brand = {}
    for o in shop.find('offers'):
        b = brand_of.get(o.findtext('categoryId'))
        if b:
            by_brand.setdefault(b, []).append(o)
    for b, offers in sorted(by_brand.items()):
        used = {o.findtext('categoryId') for o in offers}
        parents = {c.get('parentId') for c in cats if c.get('id') in used and c.get('parentId')}
        new = ET.Element('yml_catalog', root.attrib)
        sh = ET.SubElement(new, 'shop')
        ET.SubElement(sh, 'name').text = f'Údeu v2 · {b}'
        cs = ET.SubElement(sh, 'categories')
        for c in cats:
            if c.get('id') in used or c.get('id') in parents:
                cc = ET.SubElement(cs, 'category', {k: v for k, v in c.attrib.items() if k != 'brand'})
                cc.text = c.text
        ofs = ET.SubElement(sh, 'offers')
        for o in offers:
            ofs.append(o)
        ET.ElementTree(new).write(os.path.join(out_dir, f'feed-ags-{b}.yml'), encoding='UTF-8', xml_declaration=True)
        print(f'  feed-ags-{b}.yml: {len(offers)} товаров')


def main():
    refresh = '--refresh' in sys.argv
    for multi in ('feed-ags-china.yml',):
        if os.path.exists(multi):
            print(f'Разбор {multi} по маркам…')
            split_multibrand(multi)
    out_dir = '.'
    for brand in CONFIG:
        path = os.path.join(out_dir, f'feed-ags-{brand}.yml')
        if os.path.exists(path) and not refresh:
            print(f'{os.path.basename(path)}: уже есть, сбор пропущен (--refresh чтобы обновить)')
            continue
        print(f'Сбор {brand} с сайта поставщика…')
        try:
            models, items = collect(brand)
            if not items:
                raise RuntimeError('нет товаров')
            write_feed(brand, models, items, path)
        except Exception as e:
            print(f'  НЕ УДАЛОСЬ: {e}. Старый фид (если есть) оставлен.')


if __name__ == '__main__':
    main()
