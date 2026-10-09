# -*- coding: utf-8 -*-
"""Марки и модели для листингов Údeu: русские и народные названия.

BRANDS[slug] = (латиница, по-русски)
RULES[slug] = [(regex по названию категории в нижнем регистре, "народное 1|народное 2", "латиница для запросов"), ...]
Первое совпавшее правило применяется. В шаблонах можно использовать \\1, \\2 (группы регэкспа).
Для BMW и Mercedes названия строятся по кодам кузова (g05, w205) — см. bmw_aliases / mercedes_aliases.
"""
import re

BRANDS = {
    'toyota': ('Toyota', 'Тойота'), 'ford': ('Ford', 'Форд'), 'mercedes': ('Mercedes-Benz', 'Мерседес'),
    'dodge': ('Dodge', 'Додж'), 'mitsubishi': ('Mitsubishi', 'Мицубиси'), 'kia': ('Kia', 'Киа'),
    'bmw': ('BMW', 'БМВ'), 'chevrolet': ('Chevrolet', 'Шевроле'), 'vw': ('Volkswagen', 'Фольксваген'),
    'cadillac': ('Cadillac', 'Кадиллак'), 'jeep': ('Jeep', 'Джип'), 'hyundai': ('Hyundai', 'Хендай'),
    'landrover': ('Land Rover', 'Ленд Ровер'), 'greatwall': ('Great Wall', 'Грейт Волл'), 'jac': ('JAC', 'Джак'),
    'mazda': ('Mazda', 'Мазда'), 'isuzu': ('Isuzu', 'Исузу'), 'lexus': ('Lexus', 'Лексус'),
    'skoda': ('Skoda', 'Шкода'), 'haval': ('Haval', 'Хавал'), 'porsche': ('Porsche', 'Порше'),
    'audi': ('Audi', 'Ауди'), 'nissan': ('Nissan', 'Ниссан'), 'subaru': ('Subaru', 'Субару'),
    'honda': ('Honda', 'Хонда'), 'geely': ('Geely', 'Джили'), 'suzuki': ('Suzuki', 'Сузуки'),
    'tank': ('Tank', 'Танк'), 'byd': ('BYD', 'БИД'), 'renault': ('Renault', 'Рено'), 'volvo': ('Volvo', 'Вольво'),
    'changan': ('Changan', 'Чанган'), 'exeed': ('Exeed', 'Эксид'), 'chery': ('Chery', 'Чери'),
    'denza': ('Denza', 'Денза'), 'bentley': ('Bentley', 'Бентли'), 'jetour': ('Jetour', 'Джетур'),
    'infiniti': ('Infiniti', 'Инфинити'), 'gmc': ('GMC', 'Джи Эм Си'), 'mini': ('MINI', 'Мини'),
    'zeekr': ('Zeekr', 'Зикр'), 'jaguar': ('Jaguar', 'Ягуар'), 'opel': ('Opel', 'Опель'),
    'hummer': ('Hummer', 'Хаммер'), 'lynkco': ('Lynk & Co', 'Линк энд Ко'), 'genesis': ('Genesis', 'Дженезис'),
    'peugeot': ('Peugeot', 'Пежо'), 'lamborghini': ('Lamborghini', 'Ламборгини'), 'gac': ('GAC', 'ГАК'),
    'chrysler': ('Chrysler', 'Крайслер'), 'tesla': ('Tesla', 'Тесла'), 'aito': ('AITO', 'Айто'),
    'lixiang': ('Lixiang', 'Лисян'), 'brilliance': ('Brilliance', 'Бриллианс'), 'jaecoo': ('Jaecoo', 'Джейку'),
    'voyah': ('Voyah', 'Воя'), 'lincoln': ('Lincoln', 'Линкольн'), 'hongqi': ('Hongqi', 'Хончи'),
    'jetta': ('Jetta', 'Джетта'), 'seat': ('SEAT', 'Сеат'), 'pontiac': ('Pontiac', 'Понтиак'),
    'alfaromeo': ('Alfa Romeo', 'Альфа Ромео'), 'acura': ('Acura', 'Акура'),
}

RULES = {
 'toyota': [
  (r'^4runner', '4раннер|фораннер', 'toyota 4runner'),
  (r'^alphard', 'альфард', 'toyota alphard'),
  (r'^avalon', 'авалон', 'toyota avalon'),
  (r'^camry v50', 'камри 50|камри 55', 'toyota camry 55'),
  (r'^camry xv70', 'камри 70|камри 75', 'toyota camry 70'),
  (r'^camry xv80', 'камри 80', 'toyota camry 80'),
  (r'^corolla', 'королла', 'toyota corolla'),
  (r'^fj cruiser', 'фж крузер', 'toyota fj cruiser'),
  (r'^fortuner', 'фортунер', 'toyota fortuner'),
  (r'^highlander ii', 'хайлендер 2', 'toyota highlander'),
  (r'^highlander 2014', 'хайлендер 3', 'toyota highlander'),
  (r'^highlander 2020', 'хайлендер 4', 'toyota highlander'),
  (r'^hilux 2015', 'хайлюкс|хайлюкс рево', 'toyota hilux revo'),
  (r'^hilux', 'хайлюкс', 'toyota hilux'),
  (r'^lc 200', 'крузак 200|ленд крузер 200', 'toyota land cruiser 200'),
  (r'^lc 300', 'крузак 300|ленд крузер 300', 'toyota land cruiser 300'),
  (r'^lc prado 120', 'прадо 120', 'toyota prado 120'),
  (r'^lc prado 150', 'прадо 150', 'toyota prado 150'),
  (r'^lc prado 250', 'прадо 250', 'toyota prado 250'),
  (r'^rav4 \(5', 'рав 4|рав 4 50', 'toyota rav4'),
  (r'^rav4', 'рав 4', 'toyota rav4'),
  (r'^sequoia', 'секвойя', 'toyota sequoia'),
  (r'^supra', 'супра', 'toyota supra a90'),
  (r'^tacoma', 'такома', 'toyota tacoma'),
  (r'gt 86', 'тойота гт86', 'toyota gt86'),
  (r'^tundra', 'тундра', 'toyota tundra'),
 ],
 'lexus': [
  (r'^es', 'лексус ес', 'lexus es'), (r'^gs', 'лексус гс', 'lexus gs'), (r'^is', 'лексус ис', 'lexus is'),
  (r'^lx 3', 'лексус лх 570|лх 570', 'lexus lx 570'), (r'^lx 4', 'лексус лх 600|лх 600', 'lexus lx 600'),
  (r'^nx', 'лексус нх', 'lexus nx'), (r'^rx', 'лексус рх', 'lexus rx'),
 ],
 'hyundai': [
  (r'^creta', 'крета', 'hyundai creta'), (r'^elantra n', 'элантра n', 'hyundai elantra n'),
  (r'^elantra', 'элантра', 'hyundai elantra'), (r'starex', 'старекс|гранд старекс', 'hyundai starex h1'),
  (r'^grand santa fe', 'гранд санта фе', 'hyundai grand santa fe'), (r'^i40', 'хендай i40', 'hyundai i40'),
  (r'^mufasa', 'хендай муфаса', 'hyundai mufasa'), (r'^palisade', 'палисад', 'hyundai palisade'),
  (r'^santa fe 3', 'санта фе 3', 'hyundai santa fe'), (r'^santa fe 4', 'санта фе 4', 'hyundai santa fe'),
  (r'^santa fe 5', 'санта фе 5|новый санта фе', 'hyundai santa fe'), (r'^solaris', 'солярис', 'hyundai solaris'),
  (r'^sonata dn8', 'соната dn8', 'hyundai sonata'), (r'^sonata', 'соната lf', 'hyundai sonata'),
  (r'^staria', 'стария', 'hyundai staria'), (r'^tucson 2021', 'туксон 4|тусан 4', 'hyundai tucson'),
  (r'^tucson', 'туксон 3|тусан 3', 'hyundai tucson'), (r'^veloster', 'велостер', 'hyundai veloster'),
 ],
 'kia': [
  (r'^carnival', 'карнивал', 'kia carnival'), (r'^cerato', 'церато 4', 'kia cerato'), (r'^k5', 'киа к5', 'kia k5'),
  (r'^mohave', 'мохав', 'kia mohave'), (r'^optima', 'оптима 4', 'kia optima'), (r'^rio x', 'рио х лайн', 'kia rio x-line'),
  (r'^rio', 'рио 4', 'kia rio'), (r'^seltos', 'селтос', 'kia seltos'), (r'^sorento prime', 'соренто прайм', 'kia sorento prime'),
  (r'^sorento', 'соренто 4', 'kia sorento'), (r'^soul 2', 'соул 2', 'kia soul'), (r'^soul 3', 'соул 3', 'kia soul'),
  (r'^sportage 3', 'спортейдж 3', 'kia sportage'), (r'^sportage 4', 'спортейдж 4', 'kia sportage'),
  (r'^sportage nq5', 'спортейдж 5|спортейдж nq5', 'kia sportage'), (r'^stinger', 'стингер', 'kia stinger'),
  (r'^telluride', 'теллурайд', 'kia telluride'),
 ],
 'chevrolet': [
  (r'^blazer', 'блейзер', 'chevrolet blazer'), (r'^camaro', 'камаро', 'chevrolet camaro'),
  (r'^colorado', 'колорадо', 'chevrolet colorado'), (r'^corvette (c\d)', r'корвет \1', r'chevrolet corvette \1'),
  (r'^cruze', 'шевроле круз', 'chevrolet cruze'), (r'^malibu', 'малибу', 'chevrolet malibu'),
  (r'^savana', 'савана', 'chevrolet savana'), (r'^silverado', 'сильверадо', 'chevrolet silverado'),
  (r'^tahoe lll', 'тахо 900|тахо 3', 'chevrolet tahoe'), (r'^tahoe lv', 'тахо 4', 'chevrolet tahoe'),
  (r'^tahoe v', 'тахо 5|новый тахо', 'chevrolet tahoe'), (r'^tahoe', 'тахо', 'chevrolet tahoe'),
  (r'^trailblazer', 'трейлблейзер', 'chevrolet trailblazer'), (r'^traverse', 'траверс', 'chevrolet traverse'),
 ],
 'ford': [
  (r'^bronco sport', 'бронко спорт', 'ford bronco sport'), (r'^bronco', 'бронко', 'ford bronco'),
  (r'^crown', 'краун виктория', 'ford crown victoria'), (r'^ecosport', 'экоспорт', 'ford ecosport'),
  (r'^edge', 'форд эдж', 'ford edge'), (r'^explorer v ', 'эксплорер 5', 'ford explorer'),
  (r'^explorer vi', 'эксплорер 6', 'ford explorer'), (r'^f-250', 'ф250|f250', 'ford f-250'),
  (r'^f150', 'ф150|f150', 'ford f-150'), (r'^flex', 'форд флекс', 'ford flex'),
  (r'^focus iii', 'фокус 3', 'ford focus 3'), (r'^focus iv', 'фокус 4', 'ford focus 4'),
  (r'^fusion', 'фьюжн', 'ford fusion'), (r'^kuga', 'куга', 'ford kuga'), (r'^maverick', 'маверик', 'ford maverick'),
  (r'^mustang', 'мустанг', 'ford mustang'), (r'^ranger t6\.2', 'рейнджер|новый рейнджер', 'ford ranger'),
  (r'^ranger', 'рейнджер', 'ford ranger'), (r'^thunderbird', 'тандерберд', 'ford thunderbird'),
  (r'^transit', 'транзит', 'ford transit'),
 ],
 'dodge': [
  (r'trx', 'рам trx', 'dodge ram trx'), (r'rho', 'рам 1500 rho', 'ram 1500 rho'),
  (r'^ram 1500', 'рам 1500|додж рам', 'dodge ram 1500'), (r'^ram 2500', 'рам 2500|рам 3500', 'dodge ram 2500'),
  (r'^ram', 'додж рам', 'dodge ram'), (r'^caliber', 'додж калибр', 'dodge caliber'),
  (r'^challenger', 'челленджер', 'dodge challenger'), (r'^charger', 'чарджер', 'dodge charger'),
  (r'^durango', 'дуранго', 'dodge durango'), (r'^magnum', 'додж магнум', 'dodge magnum'),
  (r'^neon', 'додж неон', 'dodge neon'), (r'^viper', 'вайпер', 'dodge viper'),
 ],
 'mitsubishi': [
  (r'^3000', 'мицубиси 3000gt', 'mitsubishi 3000gt'), (r'^asx', 'мицубиси асх|асх', 'mitsubishi asx'),
  (r'^eclipse', 'эклипс кросс', 'mitsubishi eclipse cross'), (r'^l200', 'л200|l200', 'mitsubishi l200'),
  (r'^lancer', 'лансер эволюшн', 'mitsubishi lancer evolution'), (r'^outlander xl', 'аутлендер xl', 'mitsubishi outlander xl'),
  (r'^outlander', 'аутлендер', 'mitsubishi outlander'), (r'^pajero 4', 'паджеро 4', 'mitsubishi pajero 4'),
  (r'^pajero sport 2', 'паджеро спорт 2', 'mitsubishi pajero sport'), (r'^pajero sport 3', 'паджеро спорт 3', 'mitsubishi pajero sport'),
 ],
 'nissan': [
  (r'^(\d{3})z', r'ниссан \1z', r'nissan \1z'), (r'^frontier', 'ниссан фронтир', 'nissan frontier'),
  (r'^maxima', 'ниссан максима', 'nissan maxima'), (r'^murano', 'мурано', 'nissan murano'),
  (r'^pathfinder', 'патфайндер', 'nissan pathfinder'), (r'^qashqai', 'кашкай', 'nissan qashqai'),
  (r'^teana', 'теана', 'nissan teana'), (r'^titan', 'ниссан титан', 'nissan titan'),
  (r'^x-trail', 'икс трейл|х трейл', 'nissan x-trail'),
 ],
 'mazda': [
  (r'cx-30', 'мазда сх30', 'mazda cx-30'), (r'cx-50', 'мазда сх50', 'mazda cx-50'), (r'cx-3\b', 'мазда сх3', 'mazda cx-3'),
  (r'cx-5', 'мазда сх5', 'mazda cx-5'), (r'cx-9', 'мазда сх9', 'mazda cx-9'), (r'mx-5', 'мазда мх5', 'mazda mx-5'),
  (r'mazda 3', 'мазда 3', 'mazda 3'), (r'mazda 6', 'мазда 6', 'mazda 6'),
 ],
 'honda': [
  (r'^accord', 'аккорд 9', 'honda accord'), (r'^civic', 'цивик', 'honda civic'), (r'^cr-v', 'хонда срв', 'honda cr-v'),
  (r'^hr-v', 'хонда хрв', 'honda hr-v'), (r'^odyssey', 'хонда одиссей', 'honda odyssey'),
  (r'^pilot', 'хонда пилот', 'honda pilot'), (r'^ridgeline', 'хонда риджлайн', 'honda ridgeline'),
 ],
 'subaru': [
  (r'^brz', 'субару brz', 'subaru brz'), (r'^forester', 'форестер', 'subaru forester'),
  (r'wrx sti', 'импреза wrx sti', 'subaru impreza wrx sti'), (r'^impreza', 'импреза', 'subaru impreza'),
  (r'^outback', 'аутбэк', 'subaru outback'), (r'^wrx', 'субару wrx', 'subaru wrx'), (r'^xv', 'субару xv', 'subaru xv'),
 ],
 'suzuki': [(r'^jimny', 'джимни', 'suzuki jimny'), (r'^vitara', 'витара', 'suzuki vitara')],
 'vw': [
  (r'^amarok', 'амарок', 'volkswagen amarok'), (r'^beetle', 'фольксваген битл', 'volkswagen beetle'),
  (r'^caravelle', 'каравелла т6', 'volkswagen caravelle t6'), (r'^golf (\d)', r'гольф \1', r'volkswagen golf \1'),
  (r'^jetta', 'фольксваген джетта', 'volkswagen jetta'), (r'^passat cc', 'пассат сс', 'volkswagen passat cc'),
  (r'^passat b(\d)', r'пассат б\1', r'volkswagen passat b\1'), (r'^polo', 'поло седан|фольксваген поло', 'volkswagen polo'),
  (r'^scirocco', 'сирокко', 'volkswagen scirocco'), (r'multivan', 'мультивен т7', 'volkswagen multivan t7'),
  (r'^talagon', 'талагон', 'volkswagen talagon'), (r'^taos', 'фольксваген таос', 'volkswagen taos'),
  (r'^tavendor', 'тавендор', 'volkswagen tavendor'), (r'^teramont pro', 'терамонт про', 'volkswagen teramont pro'),
  (r'^teramont', 'терамонт', 'volkswagen teramont'), (r'^tayron', 'тайрон', 'volkswagen tayron'),
  (r'^tiguan', 'тигуан', 'volkswagen tiguan'), (r'^touareg iii', 'туарег 3', 'volkswagen touareg'),
  (r'^touareg ii', 'туарег 2|туарег nf', 'volkswagen touareg'), (r'^touareg i', 'туарег 1', 'volkswagen touareg'),
  (r'^viloran', 'вилоран', 'volkswagen viloran'),
 ],
 'skoda': [
  (r'^karoq', 'карок', 'skoda karoq'), (r'^kodiaq', 'кодиак', 'skoda kodiaq'), (r'octavia iii', 'октавия а7', 'skoda octavia a7'),
  (r'octavia iv', 'октавия а8', 'skoda octavia a8'), (r'^rapid', 'рапид', 'skoda rapid'), (r'^superb', 'суперб', 'skoda superb'),
 ],
 'landrover': [
  (r'^defender', 'дефендер', 'land rover defender'), (r'^discovery sport', 'дискавери спорт', 'land rover discovery sport'),
  (r'^discovery 4', 'дискавери 4', 'land rover discovery 4'), (r'^discovery 5', 'дискавери 5', 'land rover discovery 5'),
  (r'^freelander', 'фрилендер 2', 'land rover freelander 2'), (r'evoque', 'эвок|рендж ровер эвок', 'range rover evoque'),
  (r'range rover sport', 'рендж ровер спорт', 'range rover sport'), (r'velar', 'велар|рендж ровер велар', 'range rover velar'),
  (r'range rover \d-gen (l\d{3})', r'рендж ровер \1', r'range rover \1'),
 ],
 'porsche': [
  (r'^928', 'порше 928', 'porsche 928'), (r'^boxster', 'порше бокстер', 'porsche boxster'),
  (r'^carrera 991', 'порше 911|порше 991', 'porsche 911'), (r'^carrera 992', 'порше 911|порше 992', 'porsche 911'),
  (r'^cayenne e3 coupe', 'кайен купе', 'porsche cayenne coupe'), (r'^cayenne (\w+)', r'кайен \1|порше кайен', r'porsche cayenne \1'),
  (r'^cayman', 'порше кайман', 'porsche cayman'), (r'^macan', 'макан|порше макан', 'porsche macan'),
  (r'^panamera', 'панамера', 'porsche panamera'), (r'^taycan', 'тайкан', 'porsche taycan'),
 ],
 'audi': [
  (r'^([aq]\d|rs3|tt) \((\w+)\)', r'ауди \1 \2', r'audi \1 \2'), (r'^([aq]\d|rs3|tt)', r'ауди \1', r'audi \1'),
  (r'e-tron', 'ауди e-tron', 'audi e-tron'),
 ],
 'cadillac': [
  (r'^escalade esv', 'эскалейд esv', 'cadillac escalade esv'), (r'^escalade', 'эскалейд', 'cadillac escalade'),
  (r'^(ats|ct4|ct5|ct6|cts|dts|elr|srx|sts|xt4|xt5|xt6|xts)', r'кадиллак \1', r'cadillac \1'),
 ],
 'jeep': [
  (r'^grand cherokee (\w+)', r'гранд чероки \1', r'jeep grand cherokee \1'), (r'^cherokee \(xj', 'чероки xj', 'jeep cherokee xj'),
  (r'^cherokee', 'джип чероки', 'jeep cherokee'), (r'^gladiator', 'гладиатор', 'jeep gladiator'),
  (r'^renegade', 'ренегат', 'jeep renegade'), (r'^wagoneer', 'вагонир', 'jeep wagoneer'),
  (r'^wrangler (\w+)', r'вранглер \1', r'jeep wrangler \1'),
 ],
 'greatwall': [(r'king kong', 'поер кинг конг', 'great wall poer king kong'), (r'poer', 'грейт волл поер|поер', 'great wall poer')],
 'jac': [(r'[тt]8', 'джак т8|jac t8', 'jac t8 pro'), (r'^j7', 'джак j7', 'jac j7'), (r'^t6', 'джак т6', 'jac t6')],
 'isuzu': [(r'd-max', 'исузу д макс|д-макс', 'isuzu d-max')],
 'haval': [
  (r'^dargo', 'хавал дарго', 'haval dargo'), (r'^f7x', 'хавал f7x', 'haval f7x'), (r'^f7', 'хавал f7', 'haval f7'),
  (r'^jolion', 'хавал джолион|джолион', 'haval jolion'), (r'^raptor', 'хавал раптор', 'haval raptor'),
  (r'^([hm]\d)', r'хавал \1', r'haval \1'),
 ],
 'tank': [(r'tank (\d+)', r'танк \1', r'tank \1')],
 'geely': [
  (r'^atlas pro', 'атлас про', 'geely atlas pro'), (r'^atlas', 'джили атлас', 'geely atlas'), (r'^coolray', 'кулрей', 'geely coolray'),
  (r'^emgrand x7', 'эмгранд х7', 'geely emgrand x7'), (r'^emgrand', 'эмгранд', 'geely emgrand'), (r'^mk', 'джили мк', 'geely mk'),
  (r'^monjaro', 'монжаро', 'geely monjaro'), (r'^tugella', 'тугелла', 'geely tugella'),
 ],
 'changan': [
  (r'^(cs\d+)', r'чанган \1', r'changan \1'), (r'^hunter', 'чанган хантер', 'changan hunter plus'),
  (r'^uni-(\w)', r'чанган юни \1', r'changan uni-\1'),
 ],
 'chery': [(r'^arrizo 8', 'арризо 8', 'chery arrizo 8'), (r'^tiggo (\d) pro', r'тигго \1 про', r'chery tiggo \1 pro'), (r'^tiggo (\d)', r'тигго \1', r'chery tiggo \1')],
 'exeed': [(r'^(\w+)', r'эксид \1', r'exeed \1')],
 'jetour': [(r'^dashing', 'джетур дашинг', 'jetour dashing'), (r'^([tx]\d+)', r'джетур \1', r'jetour \1')],
 'byd': [(r'leopard', 'бид леопард 7|byd leopard 7', 'byd leopard 7')],
 'denza': [(r'n9', 'денза n9', 'denza n9')],
 'zeekr': [(r'^(\w+)', r'зикр \1', r'zeekr \1')],
 'volvo': [(r'^(xc\d+)', r'вольво \1', r'volvo \1'), (r'^(s90|v90)', r'вольво \1', r'volvo \1')],
 'infiniti': [(r'^qx70', 'инфинити qx70|инфинити fx', 'infiniti qx70'), (r'^qx80 \(qx56', 'инфинити qx80|инфинити qx56', 'infiniti qx80'),
              (r'^(\w+)', r'инфинити \1', r'infiniti \1')],
 'genesis': [(r'^coupe', 'хендай генезис купе', 'hyundai genesis coupe'), (r'(g70|gv80)', r'дженезис \1', r'genesis \1')],
 'gmc': [(r'^canyon', 'gmc каньон', 'gmc canyon'), (r'^sierra', 'gmc сиерра|сиерра', 'gmc sierra'), (r'^yukon', 'gmc юкон|юкон', 'gmc yukon')],
 'hummer': [(r'^(h\d)', r'хаммер \1', r'hummer \1')],
 'jaguar': [(r'^(e-pace|f-pace|xf)', r'ягуар \1', r'jaguar \1')],
 'opel': [(r'^astra (h|j|k)', r'опель астра \1', r'opel astra \1'), (r'^corsa', 'опель корса', 'opel corsa'), (r'^mokka', 'опель мокка', 'opel mokka'), (r'^zafira', 'опель зафира', 'opel zafira')],
 'peugeot': [(r'3008', 'пежо 3008', 'peugeot 3008')],
 'renault': [(r'^duster', 'рено дастер|дастер', 'renault duster'), (r'^kaptur', 'рено каптюр', 'renault kaptur'), (r'^koleos', 'рено колеос', 'renault koleos')],
 'lamborghini': [(r'urus', 'ламборгини урус|урус', 'lamborghini urus')],
 'bentley': [(r'bentayga', 'бентли бентайга', 'bentley bentayga'), (r'continental', 'бентли континенталь', 'bentley continental gt')],
 'tesla': [(r'model (\w)', r'тесла модель \1', r'tesla model \1')],
 'mini': [(r'cooper', 'мини купер', 'mini cooper'), (r'countryman', 'мини кантримен', 'mini countryman')],
 'lincoln': [(r'aviator', 'линкольн авиатор', 'lincoln aviator'), (r'mkz', 'линкольн mkz', 'lincoln mkz'), (r'navigator', 'линкольн навигатор', 'lincoln navigator')],
 'lixiang': [(r'l(\d)', r'лисян l\1|li auto l\1', r'lixiang l\1')],
 'lynkco': [(r'900', 'линк энд ко 900', 'lynk co 900')],
 'voyah': [(r'free', 'воя фри', 'voyah free')],
 'hongqi': [(r'(h\d)', r'хончи \1', r'hongqi \1')],
 'jaecoo': [(r'(j\d)', r'джейку \1', r'jaecoo \1')],
 'jetta': [(r'vs5', 'джетта vs5', 'jetta vs5')],
 'seat': [(r'ateca', 'сеат атека', 'seat ateca'), (r'leon', 'сеат леон', 'seat leon')],
 'pontiac': [(r'firebird', 'понтиак файрберд', 'pontiac firebird')],
 'alfaromeo': [(r'giulia', 'альфа ромео джулия', 'alfa romeo giulia')],
 'acura': [(r'integra', 'акура интегра', 'acura integra')],
 'gac': [(r'(gs\d)', r'гак \1', r'gac \1')],
 'brilliance': [(r'v5', 'бриллианс v5', 'brilliance v5')],
 'aito': [(r'm9', 'айто м9|aito m9', 'aito m9')],
 'chrysler': [(r'300c', 'крайслер 300с', 'chrysler 300c')],
}

DISPLAY_FIX = [(r'^LC Prado', 'Land Cruiser Prado'), (r'^LC ', 'Land Cruiser '), (r'\bll-gen\b', 'II-gen'),
               (r'\blll-gen\b', 'III-gen'), (r'\blV-gen\b', 'IV-gen'), (r'\bТ8\b', 'T8'), (r'\bМ([3458])\b', r'M\1')]

YEARS_RE = re.compile(r'\(?\s*(19\d\d|20\d\d)\s*(?:[-–—]\s*(19\d\d|20\d\d|н\.?\s?в\.?)?)?\s*\)?')


def _x_ru(s):
    """x5 -> х5 (кириллица), m3 -> м3 — так набирают в поиске."""
    s = s.lower()
    return s.replace('x', 'х', 1) if s.startswith('x') else s.replace('m', 'м', 1) if s.startswith('m') else s


def bmw_aliases(cat):
    low = cat.lower().replace('м', 'm')
    codes = re.findall(r'\b([efgiu]\d{2})\b', low)
    code = codes[0] if codes else ''
    m = re.match(r'^(\d)-серия\s+(?:(m\d)\s+)?(gt\s+)?', low)
    if m:
        series = m.group(1)
        sub = m.group(2)
        if sub:
            ru = [f'бмв {_x_ru(sub)} {code}'.strip()]
            lat = f'bmw {sub} {code}'.strip()
        else:
            ru = [f'бмв {code}'.strip(), f'бмв {series} серии']
            lat = f'bmw {series} {code}'.strip()
        return ru, lat
    m = re.match(r'^(x\dm?l?|z\d|ix|xm|i3)\b', low)
    if m:
        model = m.group(1)
        ru = [f'бмв {_x_ru(model)} {code}'.strip()]
        if model.startswith('x'):
            ru.append(f'{model} {code}'.strip())
        return ru, f'bmw {model} {code}'.strip()
    return ['бмв'], 'bmw'


def mercedes_aliases(cat):
    low = cat.lower()
    codes = re.findall(r'\b([wcxvhrnab]\d{3})\b', low)
    code = codes[0] if codes else ''
    cls = re.match(r'^([a-z]+(?:\s?gt)?)(?:[- ]class)?', low)
    cl = cls.group(1).replace(' ', '') if cls else ''
    if cl.startswith('g') and cl in ('g',):
        return [f'гелик {code}'.strip(), f'гелендваген {code}'.strip()], f'mercedes g-class {code}'.strip()
    if 'vito' in low or cl == 'v':
        return [f'мерседес вито {code}'.strip(), f'мерседес v-класс {code}'.strip()], f'mercedes vito {code}'.strip()
    if cl == 'amggt':
        return ['мерседес amg gt'], 'mercedes amg gt'
    if cl in ('a', 'b', 'c', 'e', 's', 'cl'):
        ru = [f'мерседес {code}'.strip(), f'мерседес {cl}-класс {code}'.strip()]
        if 'coupe' in low and cl == 'e':
            ru = [f'мерседес e-класс купе {code}'.strip(), f'мерседес {code}'.strip()]
        return ru, f'mercedes {cl}-class {code}'.strip()
    if cl == 'm':
        return [f'мерседес мл {code}'.strip()], f'mercedes ml {code}'.strip()
    return [f'мерседес {cl} {code}'.strip()], f'mercedes {cl} {code}'.strip()


def parse_category(slug, cat):
    """Возвращает dict: disp (как писать модель в тексте), years (str|''), y1, open (bool),
    ru (список народных форм для текста и запросов), lat (латинская форма для запросов)."""
    cat = (cat or '').strip()
    years, y1, is_open = '', '', False
    m = YEARS_RE.search(cat)
    disp = cat
    if m:
        y1 = m.group(1)
        y2 = m.group(2)
        if y2 and y2[0].isdigit():
            years = f'{y1}–{y2}'
        else:
            years, is_open = f'с {y1} года', True
        disp = (cat[:m.start()] + ' ' + cat[m.end():])
    disp = re.sub(r'\s+', ' ', disp).strip(' ,-–')
    disp = re.sub(r'\s*\((\d-(?:поколение|е поколение))\)\s*', r' \1 ', disp).strip()
    for a, b in DISPLAY_FIX:
        disp = re.sub(a, b, disp)
    disp = re.sub(r'\(([^()]*)\)', r'\1', disp)
    disp = re.sub(r'\s+', ' ', disp).strip()
    b_lat0 = BRANDS.get('bmw' if slug == 'ags-bmw' else slug, ('', ''))[0]
    if b_lat0 and disp.lower().startswith(b_lat0.lower() + ' '):
        disp = disp[len(b_lat0) + 1:]

    low = cat.lower()
    ru, lat = [], ''
    if slug in ('bmw', 'ags-bmw'):
        ru, lat = bmw_aliases(cat)
    elif slug == 'mercedes':
        ru, lat = mercedes_aliases(cat)
    else:
        for rx, ru_t, lat_t in RULES.get(slug, []):
            mm = re.search(rx, low)
            if mm:
                ru = [mm.expand(x).strip() for x in ru_t.split('|')]
                lat = mm.expand(lat_t).strip()
                break
    if not ru:
        b_lat, b_ru = BRANDS.get(slug, ('', ''))
        base = re.sub(r'\(.*?\)', '', disp).strip().lower()
        ru = [f'{b_ru.lower()} {base}'.strip()]
        lat = f'{b_lat.lower()} {base}'.strip()
    ru = [re.sub(r'\s+', ' ', r).lower() for r in ru if r]
    return {'disp': disp, 'years': years, 'y1': y1, 'open': is_open, 'ru': ru, 'lat': lat.lower()}


_UP_WORDS = {'про', 'фри', 'ли', 'энд', 'ко', 'рам', 'рав', 'воя', 'икс', 'киа', 'эдж', 'рио', 'фе', 'юни', 'мини', 'бид'}
_LOWER_WORDS = {'серии', 'и', 'купе'}


def ru_display(alias, brand_ru=''):
    """'камри 70' -> 'Камри 70', 'лексус лх 570' -> 'Лексус ЛХ 570', 'бмв х5 g05' -> 'БМВ Х5 G05'."""
    out = []
    for i, w in enumerate(alias.split()):
        m = re.fullmatch(r'([a-z]{1,3})-(класс)', w)
        if m:
            out.append(m.group(1).upper() + '-класс')
        elif w in _LOWER_WORDS and i > 0:
            out.append(w)
        elif re.search(r'\d', w) and re.search(r'[a-zа-яё]', w, re.I) and len(w) <= 6:
            out.append(w.upper())
        elif w in ('бмв', 'гак', 'срв', 'хрв', 'esv', 'brz', 'wrx', 'sti', 'gmc', 'amg', 'gt', 'xv', 'fx', 'ес', 'гс', 'ис', 'лх', 'нх', 'рх', 'мл', 'асх', 'фж'):
            out.append(w.upper())
        elif re.fullmatch(r'[a-z]+(-[a-z]+)*', w):
            out.append('-'.join(x.upper() if len(x) <= 3 else x.capitalize() for x in w.split('-')))
        elif len(w) <= 2 and re.fullmatch(r'[а-яё]+', w) and w not in _UP_WORDS:
            out.append(w.upper())
        else:
            out.append(w[:1].upper() + w[1:])
    return ' '.join(out)
