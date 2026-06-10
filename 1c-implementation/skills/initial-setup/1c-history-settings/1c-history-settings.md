---
name: 1c-history-settings
description: >
  Настраивает историю хранения данных в 1С УНФ (Aqua Delivery) через Playwright.
  Заходит в Настройки → Общие настройки → История изменений → Настроить и выставляет
  «При записи» + «Бессрочно» для 11 объектов: Расходная накладная, Приходная накладная,
  Контрагенты, Договоры, Заказ покупателя, Номенклатура, Отчет о розничных продажах,
  Чек ККМ, Чек ККМ коррекции, Чек ККМ на возврат, Маршрутный лист.
  Используй этот скилл ВСЕГДА когда нужно:
  - Настроить историю хранения данных в 1С партнёра
  - Выставить «При записи» для документов в 1С УНФ
  - Настроить версионирование объектов в 1С
  - Выполнить настройку истории изменений для нового партнёра Aqua Delivery
  Триггеры: "настрой историю хранения", "история изменений 1С", "версионирование 1С",
  "настрой при записи", упоминание URL вида server-1c.service.appsol.ru + история.
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

# Настройка истории хранения данных 1С Aqua Delivery

Настраивает версионирование объектов в 1С:УНФ для нового партнёра.
Все действия выполняются через Playwright в веб-клиенте 1С.

> **Важно:** Действия выполняет саппорт, не партнёр.

---

## Шаг 0. Данные для входа

Уточни у пользователя (если не указано):
- **URL базы** — например `https://server-1c.service.appsol.ru/romanovskirodnik/ru_RU/`
- **Пользователь** — обычно `Администратор`
- **Пароль**

---

## Шаг 1. Войти в систему

```js
await page.goto(URL);
await page.waitForTimeout(2000);
await page.getByTitle('Выбрать из списка (Ctrl+Down)').click();
await page.waitForTimeout(800);
await page.getByText('Администратор').first().click();
await page.waitForTimeout(500);
await page.getByRole('textbox', { name: 'Пароль' }).fill(PASSWORD);
await page.waitForTimeout(300);
await page.getByRole('button', { name: 'Войти' }).click();
await page.waitForTimeout(7000);
```

Если появился диалог **"Все лицензии заняты"** — нажми **Перезапустить**, подтверди `beforeunload`, войди повторно.

---

## Шаг 2. Открыть «Настройки хранения истории изменений»

```js
// Открываем меню Настройки
await page.locator('#themesCell_theme_7').click();
await page.waitForTimeout(1500);

// Кликаем "Общие настройки"
await page.locator('#cmd_0_11_txt').click();
await page.waitForTimeout(3000);

// Ищем ссылку "Настроить" у истории изменений динамически (ID меняется)
const nastroitId = await page.evaluate(() =>
  Array.from(document.querySelectorAll('[id*="НастроитьХранениеИсторииИзменений"]'))
    .find(e => e.offsetParent !== null && e.id.endsWith('#text'))?.id
);
await page.locator(`#${CSS.escape(nastroitId)}`).click();
await page.waitForTimeout(3000);
```

**Ожидаемое состояние:** открылась форма «Настройки хранения истории изменений» с таблицей объектов.

---

## Шаг 3. Универсальная функция установки версионирования

Таблица **виртуализирована** — строки рендерятся динамически. Поиск перемещает курсор, но не обновляет viewport автоматически.

```js
async function findAndSet(page, objectName) {
  // 1. Получаем ID поля поиска динамически
  const searchId = await page.evaluate(() =>
    Array.from(document.querySelectorAll('input'))
      .filter(i => i.offsetParent !== null && i.id.includes('СтрокаПоиска'))[0]?.id
  );
  if (!searchId) return `SKIP: ${objectName}`;

  // 2. Вводим поиск
  const inp = page.locator(`#${searchId}`);
  await inp.click({ clickCount: 3 });
  await inp.fill(objectName);
  await inp.press('Enter');
  await page.waitForTimeout(1000);

  // 3. Кликаем на любую видимую строку → фокус в таблицу
  const anyRow = await page.evaluate(() => {
    for (const c of document.querySelectorAll('.gridBoxText')) {
      if (c.offsetParent !== null && c.innerText?.trim() &&
          !['Объект','Когда сохранять','Срок хранения'].includes(c.innerText?.trim())) {
        const b = c.getBoundingClientRect();
        return { x: b.x + b.width/2, y: b.y + b.height/2 };
      }
    }
    return null;
  });
  if (anyRow) { await page.mouse.click(anyRow.x, anyRow.y); await page.waitForTimeout(150); }

  // 4. ArrowUp пока строка не появится в viewport (до 40 раз)
  let cell = null;
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(25);
    cell = await page.evaluate((name) => {
      for (const c of document.querySelectorAll('.gridBoxText')) {
        if (c.innerText?.trim() === name && c.offsetParent !== null) {
          const b = c.getBoundingClientRect();
          return { x: b.x + b.width/2, y: b.y + b.height/2 };
        }
      }
      return null;
    }, objectName);
    if (cell) break;
  }

  if (!cell) return `SKIP: ${objectName}`;

  // 5. Кликаем на строку и применяем "При записи"
  await page.mouse.click(cell.x, cell.y);
  await page.waitForTimeout(300);

  const btnId = await page.evaluate(() =>
    Array.from(document.querySelectorAll('[id*="ВариантВерсионированияГруппа"]'))
      .find(b => b.offsetParent !== null)?.id
  );
  if (!btnId) return `SKIP: ${objectName}`;

  await page.locator(`#${btnId}`).click();
  await page.waitForTimeout(600);

  await page.evaluate(() => {
    Array.from(document.querySelectorAll('[id*="УстановитьВариантВерсионированияВсегда"]'))
      .filter(b => b.offsetParent !== null)[0]?.click();
  });
  await page.waitForTimeout(1000);

  // 6. Проверяем результат
  const val = await page.evaluate((name) => {
    const cells = document.querySelectorAll('.gridBoxText');
    for (let i = 0; i < cells.length; i++) {
      if (cells[i].innerText?.trim() === name && cells[i].offsetParent !== null)
        return cells[i + 1]?.innerText?.trim();
    }
    return null;
  }, objectName);

  return val === 'При записи' ? `✅ ${objectName}` : `SKIP: ${objectName}`;
}
```

---

## Шаг 4. Обработать все 11 объектов

```js
const objects = [
  'Контрагенты',
  'Договоры',
  'Номенклатура',
  'Заказ покупателя',
  'Маршрутный лист',
  'Отчет о розничных продажах',
  'Приходная накладная',
  'Расходная накладная',
  'Чек ККМ',
  'Чек ККМ коррекции',
  'Чек ККМ на возврат',
];

const results = [];
const skipped = [];

for (const obj of objects) {
  const result = await findAndSet(page, obj);
  results.push(result);
  if (result.startsWith('SKIP')) skipped.push(obj);
}

console.log('Результаты:', results);
if (skipped.length > 0) console.log('Пропущены:', skipped);
```

---

## Технические особенности

### Динамические ID форм

В 1С при каждом открытии формы ID меняется (`form4_`, `form5_`, `form6_`...). Всегда искать динамически:

| Элемент | Selector |
|---|---|
| Поле поиска таблицы | `input[id*="СтрокаПоиска"]` |
| Кнопка вариантов версионирования | `[id*="ВариантВерсионированияГруппа"]` |
| Пункт "При записи" | `[id*="УстановитьВариантВерсионированияВсегда"]` |
| Ссылка "Настроить" | `[id*="НастроитьХранениеИсторииИзменений"][id$="#text"]` |
| Меню Настройки в сайдбаре | `#themesCell_theme_7` |
| Общие настройки | `#cmd_0_11_txt` |

### Виртуализация таблицы

Поиск (Ctrl+F) перемещает **курсор**, но не viewport. Рабочий алгоритм:
1. Ввести в поиск → Enter
2. Кликнуть на любую видимую строку (фокус в таблицу)
3. Нажимать `ArrowUp` пока нужная строка не появится в DOM (до 40 раз)
4. Кликнуть на найденную строку → применить кнопку toolbar

### Ошибки 1С

Если появляется «К сожалению, возникла непредвиденная ошибка»:

```js
await page.getByText('Перезапустить').click();
await page.waitForEvent('dialog').then(d => d.accept()).catch(() => {});
await page.waitForTimeout(8000);
// Повторить Шаг 1
```

---

## Итоговый чеклист

После выполнения все объекты должны иметь **Когда сохранять: При записи** / **Срок хранения: Бессрочно**:

| Объект | Раздел |
|---|---|
| Договоры | Справочники |
| Контрагенты | Справочники |
| Номенклатура | Справочники |
| Заказ покупателя | Документы |
| Маршрутный лист | Документы |
| Отчет о розничных продажах | Документы |
| Приходная накладная | Документы |
| Расходная накладная | Документы |
| Чек ККМ | Документы |
| Чек ККМ коррекции | Документы |
| Чек ККМ на возврат | Документы |
