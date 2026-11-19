r"""Сохраняет иконки ПРЕДМЕТОВ SULFUR под их внутренними именами (Item_Bread.png и т.д.).
Берёт у каждого предмета поле artwork (ссылка на спрайт) — поэтому имена совпадают с сайтом.
Нужно: pip install UnityPy pillow
Запуск: python export_item_icons.py "C:\путь\к\SULFUR" item_icons
Потом на сайте: «Выбрать папку игры» -> папка item_icons."""
import sys, os, re, json
import UnityPy

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "item_icons"
os.makedirs(out, exist_ok=True)
pat = re.compile(r"\.(assets|bundle)$|^level\d+$|^globalgamemanagers")
paths = [os.path.join(r, f) for r, _, fs in os.walk(src) for f in fs if pat.search(f)]
print("Файлов данных:", len(paths))

env = UnityPy.load(*paths)          # все файлы сразу, чтобы ссылки между ними находились
saved, nolink, fail = {}, 0, 0
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    try:
        tree = obj.read_typetree()
    except Exception:
        continue
    if "displayName" not in tree or "basePrice" not in tree or "artwork" not in tree:
        continue
    name = re.sub(r'[\\/:*?"<>|]', "_", str(tree.get("m_Name") or ""))
    ptr = tree["artwork"]
    if not name or not ptr.get("m_PathID"):
        nolink += 1
        continue
    img = None
    try:                              # основной путь: UnityPy сам находит объект по ссылке
        target = obj.read().artwork.read()
        img = target.image
    except Exception:
        try:                          # запасной: тот же файл, по PathID
            target = obj.assets_file.objects[ptr["m_PathID"]].read()
            img = target.image
        except Exception:
            fail += 1
            continue
    try:
        img.save(os.path.join(out, name + ".png"))
        saved[name] = tree.get("displayName", "")
    except Exception:
        fail += 1

with open(os.path.join(out, "_map.json"), "w", encoding="utf-8") as fh:
    json.dump(saved, fh, ensure_ascii=False, indent=1)
print(f"Сохранено иконок: {len(saved)}; без ссылки на картинку: {nolink}; не удалось: {fail} -> {out}")
