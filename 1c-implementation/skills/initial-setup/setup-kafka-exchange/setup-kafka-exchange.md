---
name: setup-kafka-exchange
description: >
  Настраивает событийный обмен с Kafka в 1С УНФ для партнёра Aqua Delivery:
  создаёт запись обмена с CRM, настраивает брокер Kafka (ydb Yandex Cloud),
  выгрузку цен (exchange-1c-price-lists, exchange-1c-massive-price-lists),
  создаёт пользователя "Обмен с Kafka" и включает регламентное задание с расписанием 120 сек.
  Используй этого агента ВСЕГДА когда нужно: настроить Kafka, событийный обмен с CRM,
  подключить брокер Kafka в 1С.
  Триггеры: "настрой kafka", "событийный обмен с kafka", "настрой брокер kafka", "обмен с kafka 1с",
  "setup kafka", "настрой обмен kafka"
tools:
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_fill_form
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_wait_for
  - mcp__playwright__browser_type
  - mcp__playwright__browser_press_key
  - mcp__playwright__browser_handle_dialog
  - mcp__playwright__browser_evaluate
---

# Настройка событийного обмена с Kafka

## Шаг 0. Данные для входа

Уточни у пользователя (если не указано):
- URL 1С (формат: https://server-1c.service.appsol.ru/{ДОМЕН}/ru_RU/)
- Логин: Администратор
- Пароль администратора
- Домен партнёра (например: romanovskirodnik)
- Пароль для пользователя "Обмен с Kafka" (обычно такой же как у Администратора)

## Шаг 1. Войти в 1С

Перейти по URL 1С, заполнить логин/пароль, нажать войти:

```
await page.goto(URL_1C);
await page.getByRole('textbox', { name: 'Пользователь' }).fill('Администратор');
await page.getByRole('textbox', { name: 'Пароль' }).fill(PASSWORD);
await page.locator('#authWindow_basic_okButton').click();
await page.getByText('Aqua Delivery').first().waitFor({ state: 'visible' });
```

## Шаг 2. Открыть Aqua Delivery → Событийный обмен с CRM

```
await page.getByText('Aqua Delivery').click();
await page.getByText('Событийный обмен с CRM').click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаг 3. Включить рычажок "Использовать событийный обмен" и нажать "Создать"

Рычажок ищется по ID с подстрокой "киСобытийныйОбменCRM":

```
// Найти и включить рычажок
const switchId = await page.evaluate(() => {
  const el = document.querySelector('[id*="киСобытийныйОбменCRM"]');
  return el?.id;
});
const switchEl = await page.evaluate(id => {
  return document.getElementById(id)?.className;
}, switchId);
if (switchEl && !switchEl.includes('select')) {
  await page.locator('#' + switchId).click();
}

// Нажать Создать (кнопка в командной панели списка)
const createBtn = await page.evaluate(() => {
  const btn = document.querySelector('[id*="ФормаСписокКоманднаяПанель"] [id*="Создать"]');
  return btn?.id;
});
await page.locator('#' + createBtn).click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаг 4. Заполнить наименование (домен партнёра)

ВАЖНО: использовать pressSequentially, не fill!

```
const nameFieldId = await page.evaluate(() => {
  const el = document.querySelector('[id*="form5"][id*="_Наименование_i0"]');
  return el?.id;
});
await page.locator('#' + nameFieldId).pressSequentially(DOMAIN_NAME);
await page.keyboard.press('Tab');
```

## Шаг 5. Включить рычажки "Включен" и "Отладка"

```
// Включен
await page.evaluate(() => {
  const el = document.getElementById('form5_Включен');
  if (el && !el.className.includes('select')) el.click();
});
// Если click() не сработал — использовать locator:
// await page.locator('#form5_Включен').click();

// Отладка
await page.evaluate(() => {
  const el = document.getElementById('form5_Отладка');
  if (el && !el.className.includes('select')) el.click();
});
```

## Шаг 6. Выбрать UID партнёра

```
await page.locator('[id*="form5_УИДПартнера_DLB"]').click();
await new Promise(f => setTimeout(f, 500));
// Выбрать первый (единственный) элемент из выпадающего списка
// Элемент появляется как [ref=...]: 386f9f9e-... — кликнуть на текст UUID
const uid = await page.evaluate(() => {
  const items = document.querySelectorAll('.cloud .selectedValue, .cloud div');
  for (const item of items) {
    if (item.textContent.match(/[0-9a-f-]{36}/)) {
      return item.textContent.trim();
    }
  }
});
if (uid) await page.getByText(uid.substring(0, 20)).click();
```

## Шаги 7-9. Создать брокер Kafka

КРИТИЧЕСКИ ВАЖНО: сначала выбрать протокол и механизм, ПОТОМ заполнять текстовые поля.

```
// 7. Открыть список брокеров
await page.locator('[id*="form5_Брокер_DLB"]').click();
await new Promise(f => setTimeout(f, 500));

// 8. Нажать плюсик создания
await page.getByTitle('Создать (F8)').click();
await new Promise(f => setTimeout(f, 2000));

// СНАЧАЛА выбираем протокол
await page.locator('[id*="form6_ПротоколБезопасности_DLB"]').click();
await page.getByText('sasl_ssl').click();

// ПОТОМ механизм
await page.locator('[id*="form6_МеханизмSASL_DLB"]').click();
await page.getByText('PLAIN').click();

// ПОТОМ заполняем текстовые поля через pressSequentially
await page.locator('#form6_Наименование_i0').click();
await page.keyboard.press('Control+a');
await page.locator('#form6_Наименование_i0').pressSequentially('ydb-01.serverless.yandexcloud.net:9093');
await page.keyboard.press('Tab');

await page.locator('#form6_СписокБрокеров_i0').click();
await page.keyboard.press('Control+a');
await page.locator('#form6_СписокБрокеров_i0').pressSequentially('ydb-01.serverless.yandexcloud.net:9093');
await page.keyboard.press('Tab');

await page.getByRole('textbox', { name: 'Имя пользователя:' }).pressSequentially('@/ru-central1/b1gk83bg1sgfs5bd6121/etnrki299qhdhptq01on');
await page.keyboard.press('Tab');

await page.getByRole('textbox', { name: 'Пароль:' }).pressSequentially('<YANDEX_API_KEY>');
await page.keyboard.press('Tab');

// Включить сертификат
await page.locator('#form6_ИспользоватьСертификат').click();

// Вставить сертификат (Яндекс Cloud CA)

await page.getByRole('textbox', { name: 'Сертификат:' }).fill(CERT);
await page.keyboard.press('Tab');

// 9. Записать и закрыть брокер
await page.locator('[id*="form6_ФормаКоманднаяПанель"]').getByTitle('Записать и закрыть').click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаг 10. Включить "Выгружать цены"

```
await page.locator('#form5_ВыгружатьЦены').click();
// Проверить что включён
const priceEnabled = await page.evaluate(() => {
  return document.getElementById('form5_ВыгружатьЦены')?.className?.includes('select');
});
```

## Шаг 11-12. Создать настройку цен (exchange-1c-price-lists)

```
// Открыть список настроек цен
await page.locator('#form5_ВыгружатьЦеныНастройка_DLB').click();
await new Promise(f => setTimeout(f, 500));

// Нажать плюсик
await page.getByTitle('Создать (F8)').click();
await new Promise(f => setTimeout(f, 2000));

// Развернуть форму если она минимизирована
const expandBtn = await page.evaluate(() => {
  const btns = document.querySelectorAll('[id*="MaximizeButton"]');
  for (const btn of btns) {
    if (btn.getBoundingClientRect().height > 0) return btn.id;
  }
});
if (expandBtn) await page.locator('#' + expandBtn).click();

// Заполнить топик
await page.getByRole('textbox', { name: 'Топик:' }).pressSequentially('exchange-1c-price-lists');
await page.keyboard.press('Tab');

// Кодировка UTF-8
await page.locator('[id*="_КодировкаТекста_DLB"]').click();
await page.getByText('UTF-8').click();

// Включить Отправка
await page.locator('[id*="form7_Отправка"]').click();
// или: await page.getByText('Отправка').click();

// Записать и закрыть настройку
await page.locator('[id*="form7_ФормаЗаписатьИЗакрыть"]').click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаг 13. Создать настройку цен (exchange-1c-massive-price-lists)

```
await page.locator('#form5_ВыгружатьЦеныНастройкаМассоваяВыгрузка_DLB').click();
await new Promise(f => setTimeout(f, 500));
await page.getByTitle('Создать (F8)').click();
await new Promise(f => setTimeout(f, 2000));

// Развернуть если нужно
const expandBtn2 = await page.evaluate(() => {
  const btns = document.querySelectorAll('[id*="MaximizeButton"]');
  for (const btn of btns) {
    if (btn.getBoundingClientRect().height > 0) return btn.id;
  }
});
if (expandBtn2) await page.locator('#' + expandBtn2).click();

await page.getByRole('textbox', { name: 'Топик:' }).pressSequentially('exchange-1c-massive-price-lists');
await page.keyboard.press('Tab');

await page.locator('[id*="_КодировкаТекста_DLB"]').click();
await page.getByText('UTF-8').click();

await page.locator('[id*="form8_Отправка"]').click();

await page.locator('[id*="form8_ФормаЗаписатьИЗакрыть"]').click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаг 14. Записать и закрыть форму "Событийный обмен с CRM"

```
// Найти кнопку "Записать и закрыть" формы form5
await page.locator('[id="form5_ФормаЗаписатьИЗакрыть"]').click();
// Если не найдена — использовать getByTitle с уточнением формы
await new Promise(f => setTimeout(f, 3000));
```

## Шаги 17-23. Создать пользователя "Обмен с Kafka"

```
// Настройки → Настройки пользователей и прав
await page.getByText('Настройки', { exact: true }).click();
await page.getByText('Настройки пользователей и прав').click();
await new Promise(f => setTimeout(f, 1000));

// Пользователи (второй элемент — первый это заголовок)
await page.locator('[id*="form9_ОткрытьПользователи#text"]').getByText('Пользователи').click();
await new Promise(f => setTimeout(f, 2000));

// Создать
await page.locator('[id*="form11_СписокКоманднаяПанель"]').getByTitle('Создать', { exact: true }).click();
await new Promise(f => setTimeout(f, 2000));

// Полное имя
await page.getByRole('textbox', { name: 'Полное имя:' }).pressSequentially('Обмен с Kafka');
await page.keyboard.press('Tab');

// Вкладка "Настройки входа"
await page.locator('[id*="thpage_form12_СтраницаНастройкиВхода"] > .tabsItemHeader > .tabsItemTitle').click();

// Убрать галочку "Показывать в списке выбора"
const showClass = await page.evaluate(() => {
  return document.getElementById('form12_ПользовательИБПоказыватьВСпискеВыбора')?.className;
});
if (showClass?.includes('select')) {
  await page.locator('#form12_ПользовательИБПоказыватьВСпискеВыбора').click();
}

// Установить пароль
await page.getByText('Установить пароль', { exact: true }).click();
await new Promise(f => setTimeout(f, 2000));
await page.getByRole('textbox', { name: 'Новый пароль: Выбрать (F4)' }).pressSequentially(KAFKA_USER_PASSWORD);
await page.keyboard.press('Tab');
await page.getByRole('textbox', { name: 'Подтверждение: Выбрать (F4)' }).pressSequentially(KAFKA_USER_PASSWORD);
await page.getByTitle('Установить пароль').click();
await new Promise(f => setTimeout(f, 1000));

// Записать
await page.getByTitle('Записать', { exact: true }).click();
await new Promise(f => setTimeout(f, 2000));

// Закрыть диалог обсуждений если появился
const noVisible = await page.evaluate(() => {
  const btn = document.querySelector('[id*="_Нет"]');
  return btn && btn.getBoundingClientRect().height > 0;
});
if (noVisible) await page.getByTitle('Нет', { exact: true }).click();

// Права доступа
await page.locator('#VW_page4item_4').click();
await new Promise(f => setTimeout(f, 1000));

// Включить в группу
await page.getByTitle('Включить в группу').click();
await new Promise(f => setTimeout(f, 2000));

// Выбрать Администраторы
await page.locator('[id*="grid_form16_ГруппыДоступа"]').getByText('Администраторы').click();
await page.locator('[id*="form16_ГруппыДоступаКоманднаяПанель"]').getByTitle('Выбрать', { exact: true }).click();
await new Promise(f => setTimeout(f, 2000));

// Вернуться на вкладку Основное (нужно для видимости кнопки "Записать и закрыть")
await page.locator('#VW_page4item_1').click();

// Записать и закрыть
await page.locator('#form12_ФормаЗаписатьИЗакрыть').click();
await new Promise(f => setTimeout(f, 2000));
```

## Шаги 24-27. Настроить регламентное задание

```
// Настройки → Обслуживание
await page.getByText('Настройки', { exact: true }).click();
await page.getByText('Обслуживание').click();
await new Promise(f => setTimeout(f, 1000));

// Регламентные операции → Регламентные и фоновые задания
await page.getByText('Регламентные операции').click();
await page.getByText('Регламентные и фоновые задания').click();
await new Promise(f => setTimeout(f, 2000));

// Найти задание в таблице — прокрутить через PageDown (2-3 раза)
// Кликнуть на первую строку для фокуса
const firstRow = await page.evaluate(() => {
  const rows = document.querySelectorAll('[id*="form18"][id*="grid"] div[class*="row"]');
  return rows[0]?.id;
});
if (firstRow) await page.locator('#' + firstRow).click();
await page.keyboard.press('Home');
await page.keyboard.press('PageDown');
await page.keyboard.press('PageDown');
await new Promise(f => setTimeout(f, 1000));

// Двойной клик на задании "Отправка получение данных Kafka"
await page.getByText('Отправка получение данных Kafka').first().dblclick();
await new Promise(f => setTimeout(f, 2000));

// Убедиться что задание включено (form19_Использование должен иметь класс "select")
const taskEnabled = await page.evaluate(() => {
  return document.getElementById('form19_Использование')?.className?.includes('select');
});
if (!taskEnabled) {
  await page.locator('#form19_Использование').click();
}

// Выбрать пользователя ОбменСK
await page.locator('[id*="form19_ИмяПользователя_DLB"]').click();
await page.getByText('ОбменСK').click();

// Расписание
await page.locator('[id*="form19_НастроитьРасписание#text"]').click();
await new Promise(f => setTimeout(f, 2000));

// Вкладка Дневное
await page.locator('#thpage_form20_Day > .tabsItemHeader > .tabsItemTitle').click();

// Поле "Повторять через" — установить 120 сек
await page.locator('#form20_DRepeatAfter_i0').click();
await page.keyboard.press('Control+a');
await page.locator('#form20_DRepeatAfter_i0').pressSequentially('120');
await page.keyboard.press('Tab');

// OK
await page.getByTitle('OK').click();
await new Promise(f => setTimeout(f, 1000));

// Записать и закрыть задание
await page.locator('[id*="form19_ФормаЗаписатьИЗакрыть"]').click();
await new Promise(f => setTimeout(f, 2000));
```

## Технические особенности

1. **Порядок заполнения брокера:** сначала выбрать протокол (sasl_ssl) и механизм (PLAIN), ПОТОМ заполнять текстовые поля (Наименование, Список брокеров). Если заполнить до выбора протокола — поля сбрасываются при смене протокола.

2. **pressSequentially вместо fill:** Поля 1С (Наименование, Список брокеров, Топик, Полное имя пользователя) требуют посимвольного ввода. Обычный fill не регистрируется системой 1С как пользовательский ввод.

3. **Форма "Настройка Кафки" может быть минимизирована:** После создания открывается как сжатая панель. Перед заполнением развернуть через кнопку "Развернуть" (MaximizeButton).

4. **Кнопка "Записать и закрыть" пользователя:** Видна только на вкладке "Основное". На вкладке "Права доступа" нужно сначала переключиться на "Основное".

5. **Диалог обсуждений:** При первой записи пользователя появляется диалог про включение обсуждений — нажать "Нет".

6. **Таблица заданий виртуализирована:** Использовать PageDown для прокрутки, затем двойной клик на строке. Поиск в поле не фильтрует список — только подсвечивает.

7. **Логин пользователя:** 1С автоматически генерирует имя для входа "ОбменСK" из полного имени "Обмен с Kafka".

8. **Задание уже включено по умолчанию:** form19_Использование имеет класс "switch zoomI select". Нужно только настроить пользователя и расписание.

9. **ID форм динамические:** form5_, form6_, form7_, form8_, form12_, form19_ и т.д. могут быть разными при следующем открытии. Искать через querySelector с подстроками имён полей.

## Итоговый чеклист

- [ ] Шаг 1: Войти в 1С
- [ ] Шаг 2: Открыть Aqua Delivery → Событийный обмен с CRM
- [ ] Шаг 3: Включить рычажок "Использовать событийный обмен", нажать "Создать"
- [ ] Шаг 4: Заполнить наименование (домен партнёра)
- [ ] Шаг 5: Включить рычажки "Включен" и "Отладка"
- [ ] Шаг 6: Выбрать UID партнёра из списка
- [ ] Шаги 7-9: Создать брокер Kafka (протокол sasl_ssl, механизм PLAIN, имя, список, SASL, сертификат)
- [ ] Шаг 10: Включить "Выгружать цены"
- [ ] Шаги 11-12: Создать настройку цен (exchange-1c-price-lists, UTF-8, Отправка)
- [ ] Шаг 13: Создать настройку цен массовой выгрузки (exchange-1c-massive-price-lists, UTF-8, Отправка)
- [ ] Шаг 14: Записать и закрыть "Событийный обмен с CRM"
- [ ] Шаги 17-23: Создать пользователя "Обмен с Kafka" (пароль, без показа в списке, группа Администраторы)
- [ ] Шаги 24-27: Настроить задание (пользователь ОбменСK, расписание 120 сек)
