---
name: disable-1c-background-jobs
description: >
  Отключает фоновые и регламентные задания в 1С УНФ (Aqua Delivery) через Playwright.
  Заходит на веб-клиент 1С, выполняет все настройки по инструкции отключения фоновых заданий
  для новых партнёров: Интернет-поддержка и сервисы, Общие настройки, Регламентные задания.
  Используй этот скилл ВСЕГДА когда нужно:
  - Отключить фоновые задания в 1С партнёра
  - Настроить новую базу 1С по инструкции Aqua Delivery
  - Зайти на сервер 1С и отключить регламентные задания
  - Выполнить начальную настройку 1С УНФ для нового партнёра
  Триггеры: "отключи фоновые задания", "настрой 1С партнёра", "зайди на сервер 1С",
  "отключи регламентные задания", упоминание URL вида server-1c.service.appsol.ru.
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

# Отключение фоновых заданий 1С Aqua Delivery

Этот агент выполняет настройку базы 1С:УНФ (Управление нашей фирмой) для нового партнёра.
Все действия выполняются через Playwright в веб-клиенте 1С.

> **Важно:** Эти действия должен выполнять саппорт, а не партнёр.

---

## Шаг 0. Получить данные для входа

Перед началом уточни у пользователя (если не указано):
- **URL базы** — например `https://server-1c.service.appsol.ru/romanovskirodnik/ru_RU/`
- **Пользователь** — обычно `Администратор`
- **Пароль**

---

## Шаг 1. Войти в систему

**Как войти через Playwright (рабочий способ):**
```js
// 1. Открыть кнопку выбора пользователя
await page.getByTitle('Выбрать из списка (Ctrl+Down)').click();
await page.waitForTimeout(800);

// 2. Кликнуть на "Администратор" в появившемся списке
await page.getByText('Администратор').click();
await page.waitForTimeout(500);

// 3. Ввести пароль
await page.getByRole('textbox', { name: 'Пароль' }).fill(PASSWORD);
await page.waitForTimeout(300);

// 4. Нажать "Войти"
await page.getByRole('button', { name: 'Войти' }).click();
await page.waitForTimeout(5000); // ждём загрузки УНФ
```

После входа откроется **1С:УНФ — Начальная страница**.

Если появился диалог **"Все лицензии заняты"** — нажми **Перезапустить**, подтверди диалог `beforeunload`, войди повторно.

---

## Шаг 2. Интернет-поддержка и сервисы

**Навигация:**
```js
await page.locator('#themesCell_theme_7').click();
await page.waitForTimeout(1500);
await page.getByText('Интернет-поддержка и сервисы').click();
await page.waitForTimeout(3000);
```

**Вспомогательная функция для скроллинга внутри формы:**
```js
await page.evaluate(() => {
  const panel = document.getElementById('form5_$scrl');
  if (panel) panel.scrollTop += N; // N = количество пикселей
});
```

### 2.1 Классификаторы и курсы валют

```js
await page.locator('label[for="form5_ГруппаКлассификаторы"]').click();
// Автоматическое обновление → "Отключено"
// Убрать галочку "Подбирать и проверять адреса через Интернет"
await page.locator('#form5_ИспользоватьВебСервисАдресов').click(); // выключить
```

**Ожидаемое состояние:** `switch zoomI` (без `select`) = выключено ✅

### 2.2 Новости

```js
await page.locator('label[for="form5_ГруппаНовости"]').click();
// form5_ВключитьРаботуСНовостями — должен быть выключен (class без "select")
```

### 2.3 Обновление версии программы

```js
await page.getByText('Обновление версии программы').click();
await page.waitForTimeout(1500);
await page.getByText('Отключена').click();
```

**Ожидаемое состояние:** радиокнопка «Отключена» выбрана (`radio zoomI select`) ✅

### 2.4 Проверка контрагентов

```js
await page.getByText('Проверка контрагентов').click();
// form5_ИспользоватьАвтоматическуюПроверкуКонтрагентов — выключен
```

### 2.5 1СПАРК Риски

```js
await page.locator('label[for="form5_ГруппаСПАРКРиски"]').click();
// form5_ИспользоватьСервисСПАРКРиски — выключен
```

### 2.6 Центр мониторинга

```js
await page.getByText('Центр мониторинга').click();
await page.waitForTimeout(1500);
await page.locator('#form5_ЦентрМониторингаЗапретитьОтправлятьДанные').click();
```

**Проверка:** `radio zoomI select` на `ЗапретитьОтправлятьДанные` = ✅

### 2.7 Внешние компоненты

```js
await page.getByText('Внешние компоненты').click();
// Радиокнопка "Отключено" (form5_ВариантОбновленияВнешнихКомпонент v0) — выбрана
```

---

## Шаг 3. Общие настройки → Поиск данных

```js
await page.locator('#themesCell_theme_7').click();
await page.waitForTimeout(1500);
await page.getByText('Общие настройки').click();
await page.waitForTimeout(3000);

await page.locator('label[for="form6_ГруппаУправлениеПолнотекстовымПоиском"]').click();
await page.waitForTimeout(1000);
// form6_ИспользоватьПолнотекстовыйПоиск — выключен (class "checkbox zoomI" без "select") ✅
```

---

## Шаг 4. Регламентные и фоновые задания

### Навигация

```js
await page.locator('#themesCell_theme_7').click();
await page.waitForTimeout(1500);
await page.getByText('Обслуживание').click();
await page.waitForTimeout(3000);

await page.getByText('Регламентные операции').click();
await page.waitForTimeout(1500);

await page.getByText('Регламентные и фоновые задания').click();
await page.waitForTimeout(4000);
```

### Универсальная функция обработки задания

```js
async function processJob(page, jobText) {
  const cell = await page.evaluate((text) => {
    const cells = document.querySelectorAll('.gridBoxText');
    for (const c of cells) {
      if (c.innerText?.trim() === text && c.offsetParent !== null) {
        const box = c.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  }, jobText);

  if (!cell) return `Not visible: ${jobText}`;

  await page.mouse.dblclick(cell.x, cell.y);
  await page.waitForTimeout(2500);

  const sw = await page.evaluate(() => {
    for (const s of document.querySelectorAll('.switch')) {
      if (s.offsetParent !== null) return { id: s.id, cls: s.className };
    }
    return null;
  });
  if (!sw) return `No switch: ${jobText}`;

  const saveId = await page.evaluate(() => {
    for (const b of document.querySelectorAll('[id$="_ЗаписатьИЗакрыть"]')) {
      if (b.offsetParent !== null) return b.id;
    }
    return null;
  });

  if (sw.cls.includes('select')) {
    await page.locator(`#${sw.id}`).click();
    await page.waitForTimeout(400);
    await page.locator(`#${saveId}`).click();
    await page.waitForTimeout(2000);
    return `✅ Disabled: ${jobText}`;
  } else {
    await page.locator(`#${saveId}`).click();
    await page.waitForTimeout(1000);
    return `⏭ Already off: ${jobText}`;
  }
}
```

### Навигация по таблице

Таблица **виртуализирована** — строки рендерятся динамически. Скроллинг только через клавиши:

```js
await page.locator('#form8_ТаблицаРегламентныеЗадания').click();
await page.keyboard.press('Home');
await page.waitForTimeout(400);

// Скроллить стрелками до нужной строки
for (let i = 0; i < N; i++) {
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(20);
}

// Получить текущие видимые строки
const texts = await page.evaluate(() =>
  Array.from(document.querySelectorAll('.gridBoxText'))
    .filter(el => el.offsetParent !== null)
    .map(el => el.innerText?.trim())
    .filter(t => t && !['Наименование','Состояние','Дата окончания','<не определено>'].includes(t))
);
```

**Примерные позиции по стрелкам от начала (Home):**

| Задание | ~шагов вниз |
|---|---|
| 1С:Номенклатура. Выгрузка... | 1 |
| Загрузка курсов валют | 4 |
| Заполнение контрагентов на мониторинге СПАРК | 7 |
| Обновление индексов СПАРК Риски | ~28 |
| Обновление регламентированных отчетов | ~33 |
| Обновление факторов рисков СПАРК | ~35 |
| Получение уведомлений Монитора Портала 1С:ИТС | ~50 |
| Проверка ведения учета | ~52 |
| Синхронизация рекомендаций 1С:Плюс | ~58 |
| Синхронизация с 1С:Плюс | ~59 |

> Позиции приблизительные — зависят от конкретной базы. Всегда проверяй видимые строки перед открытием.

### Список заданий для отключения

Пройди по каждому заданию. Если задание не найдено в базе — пропусти его.

```
1.  1С:Номенклатура. Выгрузка номенклатуры в электронные каталоги
2.  Загрузка курсов валют
3.  Заполнение контрагентов на мониторинге СПАРК Риски
4.  Обновление внешних компонент              ← может отсутствовать
5.  Обновление индексов СПАРК Риски
6.  Обновление настроек участников СБП        ← может отсутствовать
7.  Обновление регламентированных отчетов
8.  Обновление факторов рисков СПАРК
9.  Очистка замеров времени                   ← может отсутствовать
10. Получение уведомлений Монитора Портала 1С:ИТС
11. Проверка ведения учета
12. Синхронизация рекомендаций 1С:Плюс
13. Синхронизация с 1С:Плюс
```

---

## Технические особенности веб-клиента 1С

### Идентификаторы элементов

| Элемент | ID паттерн |
|---|---|
| Переключатель задания | `formN_Использование` (N меняется: 9, 10, 11, 13...) |
| Кнопка сохранения | `formN_ЗаписатьИЗакрыть` |
| Скроллируемая панель настроек | `form5_$scrl` |
| Меню "Настройки" в сайдбаре | `#themesCell_theme_7` |
| Таблица заданий | `#form8_ТаблицаРегламентныеЗадания` |

### Состояния переключателей

```
switch zoomI select  → включён  (нужно кликнуть чтобы выключить)
switch zoomI         → выключен ✅
radio zoomI select   → выбрана эта радиокнопка
checkbox zoomI       → чекбокс выключен (без select)
```

### Скроллинг

- Панель настроек (`form5_$scrl`) — через `element.scrollTop`
- Таблица заданий — **только через клавиши** `ArrowDown`/`ArrowUp`/`Home`/`End`
- `window.scrollBy` и `page.mouse.wheel` **не работают** в 1С

---

## Итоговый чеклист

После выполнения всех шагов сообщи результат по чеклисту:

**Интернет-поддержка и сервисы:**
- [ ] Классификаторы → «Отключено»
- [ ] «Подбирать адреса через Интернет» → выкл
- [ ] Новости → выкл
- [ ] Обновление версии → «Отключена»
- [ ] Проверка контрагентов → выкл
- [ ] 1СПАРК Риски → выкл
- [ ] Центр мониторинга → «Запретить отправку сведений»
- [ ] Внешние компоненты → «Отключено»

**Общие настройки:**
- [ ] Полнотекстовый поиск данных → выкл

**Регламентные задания** (все найденные в базе):
- [ ] 1С:Номенклатура. Выгрузка...
- [ ] Загрузка курсов валют
- [ ] Заполнение контрагентов на мониторинге СПАРК
- [ ] Обновление индексов СПАРК Риски
- [ ] Обновление регламентированных отчетов
- [ ] Обновление факторов рисков СПАРК
- [ ] Получение уведомлений Монитора Портала 1С:ИТС
- [ ] Проверка ведения учета
- [ ] Синхронизация рекомендаций 1С:Плюс
- [ ] Синхронизация с 1С:Плюс
