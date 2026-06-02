#!/usr/bin/env python3
"""
fill_docs.py — Заполняет шаблоны «Политика конфиденциальности» и
«Согласие на обработку персональных данных» реквизитами организации.

Использование:
    python3 fill_docs.py <requisites.json> <output_dir> <templates_dir>
"""

import json, re, sys, zipfile
from datetime import datetime
from pathlib import Path

MONTHS_RU = {
    1:"января",2:"февраля",3:"марта",4:"апреля",5:"мая",6:"июня",
    7:"июля",8:"августа",9:"сентября",10:"октября",11:"ноября",12:"декабря",
}

# ---------------------------------------------------------------------------
# Склонение ФИО
# ---------------------------------------------------------------------------

def _detect_gender(fio):
    """Определяем пол по отчеству или окончанию фамилии."""
    parts = fio.split()
    if len(parts) >= 3:
        patr = parts[2].lower()
        if patr.endswith(('овна', 'евна', 'ична', 'вна', 'чна')):
            return 'femn'
        if patr.endswith(('ович', 'евич', 'вич', 'ич')):
            return 'masc'
    surname = parts[0].lower()
    if surname.endswith(('ова', 'ева', 'ина', 'ская', 'цкая')):
        return 'femn'
    return 'masc'


def decline_fio(fio, case='datv'):
    """Склоняет ФИО в нужный падеж с учётом пола.
    Требует pymorphy2. Если не установлен — возвращает ФИО без изменений."""
    try:
        import pymorphy2
        morph = pymorphy2.MorphAnalyzer()
    except ImportError:
        return fio

    gender = _detect_gender(fio)
    result = []
    for word in fio.split():
        parsed = morph.parse(word)
        declined = None
        for p in parsed:
            if gender in str(p.tag):
                inflected = p.inflect({case})
                if inflected:
                    declined = inflected.word.capitalize()
                    break
        if not declined:
            for p in parsed:
                inflected = p.inflect({case})
                if inflected:
                    declined = inflected.word.capitalize()
                    break
        result.append(declined or word)
    return ' '.join(result)


# ---------------------------------------------------------------------------
# Утилиты docx
# ---------------------------------------------------------------------------

def get_xml(path):
    with zipfile.ZipFile(path, "r") as z:
        return z.read("word/document.xml").decode("utf-8")


def save_docx(template, output, xml):
    with zipfile.ZipFile(template, "r") as zin:
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, xml.encode("utf-8"))
                else:
                    zout.writestr(item, zin.read(item.filename))


def remove_highlights(content):
    return re.sub(r"\s*<w:highlight[^/]*/>\n?", "", content)


def replace_ogrn(content, r):
    """Заменяет ОГРНИП/ОГРН и убирает осиротевший прогон ':'"""
    label = "ОГРН" if r["org_type"] == "ООО" else "ОГРНИП"
    val = f"{label}: {r['ogrn']},"
    content = content.replace(">ОГРНИП<", f">{val}<", 1)
    esc = re.escape(f">{val}<")
    content = re.sub(
        esc + r"([\s\S]{1,600}?)<w:t[^>]*>:<\/w:t>",
        lambda m: f">{val}<" + m.group(1) + '<w:t xml:space="preserve"></w:t>',
        content, count=1
    )
    return content


# ---------------------------------------------------------------------------
# Заполнение Политики конфиденциальности
# ---------------------------------------------------------------------------

def fill_privacy(content, r):
    content = remove_highlights(content)

    if r["org_type"] == "ООО":
        content = content.replace(
            "— Индивидуальный предприниматель «",
            "— Общество с ограниченной ответственностью «")
    else:
        content = content.replace(
            "— Индивидуальный предприниматель «",
            "— Индивидуальный предприниматель ")

    content = content.replace(">0000<", f">{r['org_name']}<")

    if r["org_type"] == "ИП":
        content = content.replace(">»,<", ">,<", 1)

    content = content.replace(">https://11111.ru<", f">https://{r['website']}<")
    content = content.replace(">1111111<", f">{r['address']}<")

    inn_str = f"{r['inn']}, КПП: {r['kpp']}," if r["org_type"] == "ООО" and r.get("kpp") else f"{r['inn']},"
    content = content.replace(">000000000,<", f">{inn_str}<")

    content = replace_ogrn(content, r)
    content = content.replace(">000000000<", f">{r['phone']}<")
    content = content.replace("> ______.ru<", f"> {r['email']}<")

    for val in [r["director"], r["email"], r["address"], r["org_name"], r["phone"]]:
        content = content.replace(">___________<", f">{val}<", 1)

    content = re.sub(
        r">___________<([\s\S]{0,600}?)<w:t[^>]*>\.ru, принадлежащий",
        lambda m: f">{r['website']}<" + m.group(1) + "<w:t xml:space=\"preserve\">, принадлежащий",
        content, count=1
    )

    if r["org_type"] == "ООО":
        content = content.replace(">, ИП <", ">, ООО <")

    content = content.replace(">___________,<", f">{r['website']},<")

    for s in [">10.03.2026<", ">28.04.2026<", ">19.12.2024<", ">15.01.2025<", ">14.01.2025<"]:
        content = content.replace(s, f">{r['date_short']}<")
    for s in [">10 марта 2026 г.<", ">28 апреля 2026 г.<",
              ">19 декабря 2024 г.<", ">15 января 2025 г.<", ">14 января 2025 г.<"]:
        content = content.replace(s, f">{r['date_long']}<")

    return content


# ---------------------------------------------------------------------------
# Заполнение Согласия на обработку персональных данных
# ---------------------------------------------------------------------------

def fill_consent(content, r):
    content = remove_highlights(content)

    if r["org_type"] == "ООО":
        content = content.replace(
            ">Индивидуальному предпринимателю<",
            ">Обществу с ограниченной ответственностью<")
        content = content.replace(">123<", f">{r['org_name']}<")
        content = content.replace(">«111111».<", f">«{r['org_name']}».<")
    else:
        fio_datv = decline_fio(r["org_name"], case='datv')
        content = content.replace("> «<", "> <", 1)
        content = content.replace(">123<", f">{fio_datv}<")
        content = content.replace(">» (ИНН: <", "> (ИНН: <", 1)
        content = content.replace(">«111111».<", f">{r['org_name']}.<")

    content = content.replace(">000000000<", f">{r['inn']}<")
    content = content.replace(">_______<", f">{r['address']}<")
    content = content.replace(">https://111111.ru<", f">https://{r['website']}<")
    content = content.replace(">1111@1111.ru<", f">{r['email']}<")
    content = content.replace(">_________<", f">{r['address']}<")

    if r["org_type"] == "ООО":
        content = content.replace(">, ИП <", ">, ООО <")

    return content


# ---------------------------------------------------------------------------
# Вспомогательная функция: извлечение города из адреса
# ---------------------------------------------------------------------------

def extract_city(address):
    m = re.search(r'г\.\s+([^,]+)', address)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Заполнение Пользовательского соглашения о порядке покупки товаров
# ---------------------------------------------------------------------------

def fill_agreement(content, r):
    content = remove_highlights(content)

    today = r["_today"]
    date_edition = f"{today.day} {MONTHS_RU[today.month]} {today.year} года."
    content = re.sub(
        r">Редакция от \d+ \w+ \d{4} года\.<",
        f">Редакция от {date_edition}<",
        content, count=1
    )

    city = extract_city(r["address"])
    if city:
        content = content.replace(">Сыктывкар<", f">{city}<", 1)

    if r["org_type"] == "ООО":
        content = content.replace(
            ">Обществом с ограниченной ответственностью «Артезианский источник-Сервис»<",
            f">Обществом с ограниченной ответственностью «{r['org_name']}»<"
        )
    else:
        fio_ablt = decline_fio(r["org_name"], case="ablt")
        content = content.replace(
            ">Обществом с ограниченной ответственностью «Артезианский источник-Сервис»<",
            f">Индивидуальным предпринимателем {fio_ablt}<"
        )

    content = content.replace(">https://artesian11.ru <", f">https://{r['website']} <")
    content = content.replace(">https://artesian11.veel.shop<", f">https://{r['website']}<")

    if r["org_type"] == "ИП":
        content = content.replace(
            ">Общество с ограниченной ответственностью <",
            ">Индивидуальный предприниматель <", 1
        )

    if r["org_type"] == "ООО":
        content = content.replace(
            ">«Артезианский источник-Сервис»,<",
            f">«{r['org_name']}»,<"
        )
    else:
        content = content.replace(
            ">«Артезианский источник-Сервис»,<",
            f">{r['org_name']},<"
        )

    content = content.replace(
        "> 167004, Республика Коми, г. Сыктывкар, ул. Маркова 35/1,<",
        f"> {r['address']},<"
    )
    content = content.replace(
        ">167004, Республика Коми, г. Сыктывкар, ул. Маркова 35/1,<",
        f">{r['address']},<"
    )

    content = content.replace(">1101049822,<", f">{r['inn']},<")

    if r["org_type"] == "ИП":
        content = re.sub(
            r"<w:p\b[^>]*>(?:(?!</w:p>).)*?<w:t[^>]*>КПП: </w:t>(?:(?!</w:p>).)*?</w:p>",
            "", content, count=1, flags=re.DOTALL
        )
    else:
        content = content.replace(">110101001,<", f">{r.get('kpp', '')} ,<")

    if r["org_type"] == "ИП":
        content = content.replace(">ОГРН: <", ">ОГРНИП: <", 1)
    content = content.replace(">1061101040186,<", f">{r['ogrn']},<")

    content = content.replace(
        ">8(8212) 21-17-09, 8(8212) 46-96-97,<",
        f">{r['phone']},<"
    )

    if r["org_type"] == "ООО":
        content = content.replace(
            ">Генеральный директор: <",
            f">Генеральный директор: {r['director']}<"
        )
    else:
        content = content.replace(
            ">Генеральный директор: <",
            f">Индивидуальный предприниматель {r['org_name']}<"
        )

    return content


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 4:
        print("Использование: fill_docs.py <requisites.json> <output_dir> <templates_dir>")
        sys.exit(1)

    req_path, output_dir, tmpl_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(req_path, encoding="utf-8") as f:
        r = json.load(f)

    today = datetime.today()
    r["date_short"] = today.strftime("%d.%m.%Y")
    r["date_long"] = f"{today.day} {MONTHS_RU[today.month]} {today.year} г."

    tag = r["org_name"].split()[0] if r["org_type"] == "ИП" else r["org_name"]

    priv_tmpl = str(tmpl_dir / "Политика конфиденциальности.docx")
    priv_out = str(output_dir / f"Политика конфиденциальности ({tag}).docx")
    save_docx(priv_tmpl, priv_out, fill_privacy(get_xml(priv_tmpl), r))
    print(f"✓ {priv_out}")

    con_tmpl = str(tmpl_dir / "Согласие на обработку персональных данных.docx")
    con_out = str(output_dir / f"Согласие на обработку персональных данных ({tag}).docx")
    save_docx(con_tmpl, con_out, fill_consent(get_xml(con_tmpl), r))
    print(f"✓ {con_out}")

    agr_tmpl = tmpl_dir / "Пользовательское соглашение о порядке покупки товаров.docx"
    if agr_tmpl.exists():
        r["_today"] = datetime.today()
        agr_out = str(output_dir / f"Пользовательское соглашение ({tag}).docx")
        save_docx(str(agr_tmpl), agr_out, fill_agreement(get_xml(str(agr_tmpl)), r))
        print(f"✓ {agr_out}")

    print(f"\nГотово! Сохранено в: {output_dir}")


if __name__ == "__main__":
    main()
