# «Егерь» — ручной редизайн: план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Перевести лаунчер «Егерь» на ручной монохромно-латунный стиль по референсу, убрать управление модами, заменить иконку и выпустить 0.3.0 с работающим автообновлением.

**Architecture:** Новый стиль `Theme.Style.HAND` рисует фон, бланки и элементы через Java2D-примитивы в `Ink.java` и ветки существующих компонентов `UI.java`. Компоновка `LauncherApp` перестраивается в плакат: слово «ЕГЕРЬ» и бланк слева, иллюстрация справа. Ассеты (иллюстрация, бумага, шрифты, иконка) кладутся в jar, поэтому автообновление остаётся самодостаточным.

**Tech Stack:** Java 21, Swing/Java2D, PowerShell-сборка `build.ps1`, Python/Pillow для ассетов, GitHub CLI для релиза. Внешних зависимостей нет.

**Spec:** `docs/superpowers/specs/2026-11-07-eger-launcher-redesign-design.md`

## Global Constraints

- Окно: 920×560, undecorated, radius 2; настройки 760×620.
- Палитра `hand`: paper `#C9C5B9`, paper.light `#E4E0D5`, paper.shadow `#A7A395`, ink `#1C1B18`, ink.soft `#3B3933`, muted `#6A665B`, brass `#A07C3C`, brass.hover `#C09A52`, on.brass `#14130F`, online `#A07C3C`, offline `#1C1B18`.
- Заголовок бланка: **ДЕГУСТАЦИЯ МАЙОНЕЗА**. Кнопка: **НА ДЕГУСТАЦИЮ**. Печать: **ОПЫТНАЯ ПАРТИЯ**. Загрузка: **ПРИЁМКА**. Версия: `0.3.0`.
- В сгенерированных картинках нет текста. Все надписи рисуются кодом.
- Никаких новых библиотек, никакого изменения логики `GameInstaller`, `GameLauncher`, `JavaRuntime`, `SelfUpdate`, `Net`, `ModpackSync`.
- Незакоммиченные правки Linux/macOS в `Config.java`, `GameInstaller.java`, `GameLauncher.java`, `JavaRuntime.java`, `SelfUpdate.java` и файлы `build.sh`, `tools/stub/EgerStub.sh` сохранить. Коммитить только явно перечисленные пути.
- Ассеты входят в jar; внешняя папка `theme/` рядом с jar/exe имеет приоритет.
- Внешний `theme.properties` применяется только при `theme.revision >= 2`.
- Итоговая сборка: `build.ps1` (JDK `C:\Program Files\Java\jdk-21`), публикация: `build.ps1 -Publish` в `exxtezys/eger-launcher`.
- Проверки ручные: автотестов в проекте нет. Каждая задача заканчивается сборкой и проверкой поведения.

## Review Focus

1. **Старый профиль.** Игрок с `uiStyle=clean` и старым внешним `theme.properties` запускает 0.3.0: тема не падает, стиль однократно становится `hand`, оливковый фон не мелькает.
2. **Запуск только из jar.** `java -jar build\EliumLauncher.jar` без папки `theme/` рядом: видны иллюстрация, бумага, шрифты и новая иконка, ничего не «missing».
3. **Длинная ошибка.** Многострочное сообщение (URL манифеста + причина) целиком читается в «ДОНЕСЕНИИ», переносится и прокручивается, кнопка не уезжает.
4. **Масштаб Windows.** 125 % и 150 %: текст, поля, кнопки и шаги не обрезаются и не наезжают.
5. **Битый ассет.** Нет или повреждён `hand-hero.png`, нет файла шрифта: приложение запускается, рисует бумажный фон и системный шрифт, пишет причину в stderr, не падает.

Каждая строка проверяется в задаче, где появляется соответствующий код (указано в шагах).

---

### Task 1: Удалить управление модами

**Files:**
- Delete: `src/com/elium/launcher/AdminPanel.java`
- Delete: `src/com/elium/launcher/CustomMods.java`
- Modify: `src/com/elium/launcher/Config.java:94-125`
- Modify: `src/com/elium/launcher/LauncherApp.java:7, 325-361, 487`

**Interfaces:**
- Produces: `Config.saveUser(String nick, int ramMb, boolean autoConnect)` — без параметра папки модов.
- Produces: `Config.saveUserSettings(String nick, int ramMb, boolean autoConnect, int maxDownloads, boolean autoUpdate, String modpackUrlOverride, String extraJvmArgs, String uiStyle, boolean keepLogs, String serverHostOverride, int serverPortOverride)`.
- Produces: `Config.uiStyle()` по умолчанию `"hand"`.
- Produces: однократная миграция в конструкторе `Config`: если ключа `uiStyleRevision` нет, выставить `uiStyle=hand`, `uiStyleRevision=1` и сохранить файл best-effort (ошибку записи только логировать).

- [ ] **Step 1: Удалить `AdminPanel.java` и `CustomMods.java`**

```powershell
Remove-Item src\com\elium\launcher\AdminPanel.java, src\com\elium\launcher\CustomMods.java
```

- [ ] **Step 2: Убрать `customModsDir()` и параметр из `Config`**

Удалить метод `customModsDir()`, убрать `customModsDir` из сигнатуры `saveUserSettings`, из вызова `saveUser`, из `user.setProperty`; в комментарии класса заменить «custom mods» на «UI style». В конструкторе после чтения `launcher-user.properties` добавить миграцию стиля.

- [ ] **Step 3: Убрать UI и вызов синхронизации из `LauncherApp`**

Удалить импорт `JFileChooser`, блок `customDirLabel`/`customDirField`/`customDirBtn`, кнопку `admin`, локальную переменную `customDir` и её передачу в `saveUserSettings`, вызов `CustomMods.sync(cfg, p)`.

- [ ] **Step 4: Проверить, что ссылок не осталось**

Run:

```powershell
Select-String -Path src\com\elium\launcher\*.java -Pattern "CustomMods|AdminPanel|customMods|custom-mods" 
```

Expected: пусто.

- [ ] **Step 5: Собрать и запустить**

Run:

```powershell
.\build.ps1
java -Delium.dir="$env:TEMP\eger-check" -jar build\EliumLauncher.jar
```

Expected: сборка без ошибок, окно открывается, в настройках нет блока custom-модов, в `<temp>\eger-check` нет папки `custom-mods`.

- [ ] **Step 6: Коммит**

```powershell
git add src/com/elium/launcher/Config.java src/com/elium/launcher/LauncherApp.java
git rm src/com/elium/launcher/AdminPanel.java src/com/elium/launcher/CustomMods.java
git commit -m "refactor: убрать управление custom-модами"
```

---

### Task 2: Фундамент темы `hand`

**Files:**
- Modify: `src/com/elium/launcher/Theme.java:28-98, 104-199`
- Modify: `src/com/elium/launcher/theme.properties`
- Modify: `src/com/elium/launcher/Config.java` (только если миграция ещё не сделана в Task 1)

**Interfaces:**
- Produces: `Theme.Style.HAND`.
- Produces: `Theme.handHero`, `Theme.handPaper`, `Theme.handIcon` (`BufferedImage`, nullable).
- Produces: выбор палитры: `HAND` читает `color.hand.*`, остальные — `color.*`.
- Produces: ключи `theme.revision`, `hand.hero`, `hand.paper`, `hand.icon`, `font.display.file`, `font.body.file`.
- Produces: `Theme.font(int style, float size)` использует трафаретный шрифт для `Font.BOLD` и машинописный для остальных, как и раньше.

- [ ] **Step 1: Добавить стиль и порядок чтения**

В `Theme` читать `style` до цветов. Добавить `HAND` в enum. Для `HAND` брать префикс `color.hand.`, иначе `color.`.

- [ ] **Step 2: Добавить ревизию внешней темы**

Читать встроенный `theme.properties`, затем внешний во временный `Properties ext`. Если `ext` содержит `theme.revision >= 2` — `p.putAll(ext)`, иначе напечатать в stderr `theme: внешняя тема устарела (нужна revision 2), игнорирую` и не применять.

- [ ] **Step 3: Добавить ассеты и шрифты**

Поля `handHero`, `handPaper`, `handIcon` читать из `hand.hero`, `hand.paper`, `hand.icon`. Шрифты: `font.display.file` и `font.body.file` грузить через `Font.createFont`, регистрировать, при ошибке писать в stderr и падать на `font`/`font.body`. `baseFont` — display, `bodyFont` — body.

- [ ] **Step 4: Обновить `theme.properties`**

Добавить `theme.revision=2`, `ui.style=hand`, `hand.hero=hand-hero.png`, `hand.paper=paper.png`, `hand.icon=hand-icon.png`, `font.display.file=fonts/RussoOne-Regular.ttf`, `font.body.file=fonts/PTMono-Regular.ttf`, блок `color.hand.*` из Global Constraints. Старые `color.*` оставить без изменений.

- [ ] **Step 5: Проверить миграцию и ревизию**

Run:

```powershell
$d = "$env:TEMP\eger-migrate"; Remove-Item -Recurse -Force $d -ErrorAction SilentlyContinue; New-Item -ItemType Directory $d | Out-Null
"uiStyle=clean" | Set-Content "$d\launcher-user.properties"
.\build.ps1
java -Delium.dir="$d" -jar build\EliumLauncher.jar
```

Expected: окно в стиле `hand`, в `launcher-user.properties` появились `uiStyle=hand` и `uiStyleRevision=1`. Затем положить рядом с jar `theme.properties` с `theme.revision=1` и убедиться, что stderr содержит сообщение об игнорировании, а вид остаётся светлым.

- [ ] **Step 6: Коммит**

```powershell
git add src/com/elium/launcher/Theme.java src/com/elium/launcher/theme.properties src/com/elium/launcher/Config.java
git commit -m "feat: стиль hand и палитра темы"
```

---

### Task 3: Ассеты — бумага, иконка, иллюстрация, шрифты

**Files:**
- Modify: `tools/make_theme.py`
- Create: `theme/paper.png`, `theme/hand-icon.png`, `icon.ico`, `theme/hand-hero.png`
- Create: `theme/fonts/RussoOne-Regular.ttf`, `theme/fonts/PTMono-Regular.ttf`, `theme/fonts/OFL-RussoOne.txt`, `theme/fonts/OFL-PTMono.txt`

**Interfaces:**
- Produces: `paper.png` 512×512, тайл, светлая бумага с зерном.
- Produces: `hand-icon.png` 256×256 и `icon.ico` с размерами 16, 24, 32, 48, 64, 128, 256.
- Produces: `hand-hero.png` 1400×1800 RGBA, тушь, без текста.
- Produces: шрифты с кириллицей и лицензией OFL.

- [ ] **Step 1: Добавить в `make_theme.py` функции `paper()` и `hand_icon()`**

`paper()`: светлая база `#C9C5B9`, многооктавный шум, волокна, редкие пятна, без текста. `hand_icon()`: бумажный квадрат, рамка `#1C1B18` 1 px, латунная дуга, геометрическая трафаретная «Е» (вертикаль + три горизонтали с перемычками). Для 16–32 px — без дуги и с утолщённой буквой. Сохранить `icon.ico` через `Image.save(..., sizes=[...])`. Вызвать обе функции из `__main__`.

- [ ] **Step 2: Сгенерировать бумагу и иконку**

Run:

```powershell
python tools\make_theme.py
python -c "from PIL import Image; im=Image.open('icon.ico'); print(sorted(im.info['sizes']))"
```

Expected: `[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]`.

- [ ] **Step 3: Сгенерировать иллюстрацию**

Промпт: «black ink drawing, hand holding an open glass jar of mayonnaise, retro-futurist Soviet 1939, orbital rings, stars, small airship, wheat ears, grayscale, transparent background, no text, no letters, no watermark». Сохранить как `theme/hand-hero.png` 1400×1800 RGBA. Проверить глазами: нет букв, нет водяных знаков, рука и банка читаются.

- [ ] **Step 4: Скачать шрифты с кириллицей**

```powershell
New-Item -ItemType Directory -Force theme\fonts | Out-Null
Invoke-WebRequest "https://github.com/google/fonts/raw/main/ofl/russoone/RussoOne-Regular.ttf" -OutFile theme\fonts\RussoOne-Regular.ttf
Invoke-WebRequest "https://github.com/google/fonts/raw/main/ofl/ptmono/PTM55FT.ttf" -OutFile theme\fonts\PTMono-Regular.ttf
Invoke-WebRequest "https://github.com/google/fonts/raw/main/ofl/russoone/OFL.txt" -OutFile theme\fonts\OFL-RussoOne.txt
Invoke-WebRequest "https://github.com/google/fonts/raw/main/ofl/ptmono/OFL.txt" -OutFile theme\fonts\OFL-PTMono.txt
```

Expected: четыре файла ненулевого размера. Проверить, что оба шрифта содержат кириллицу (открыть в системе или через Python `fontTools`, если доступен).

- [ ] **Step 5: Проверить fallback**

Run: временно переименовать `theme/hand-hero.png`, запустить `java -jar build\EliumLauncher.jar`, убедиться, что окно открывается на бумажном фоне без иллюстрации. Вернуть файл.

- [ ] **Step 6: Коммит**

```powershell
git add tools/make_theme.py theme/paper.png theme/hand-icon.png theme/hand-hero.png theme/fonts icon.ico
git commit -m "feat: ассеты ручного стиля и иконка"
```

---

### Task 4: Чернильные примитивы и базовые контролы

**Files:**
- Create: `src/com/elium/launcher/Ink.java`
- Modify: `src/com/elium/launcher/UI.java:48-74, 126-328`

**Interfaces:**
- Produces: `Ink.tornBorder(Graphics2D g, float x, float y, float w, float h, Color ink, long seed)`.
- Produces: `Ink.hatch(Graphics2D g, Shape clip, float angle, float gap, Color ink)`.
- Produces: `Ink.spaced(Graphics2D g, String text, float x, float y, float tracking)`.
- Produces: `Ink.inkText(Graphics2D g, String text, Font font, float x, float y, long seed)` — текст с эрозией, кэш по строке/кеглю.
- Produces: `Ink.orbit(Graphics2D g, float cx, float cy, float rx, float ry, float phase, Color ink)`.
- Produces: `UI.Card`, `UI.Btn`, `UI.Field` с ветками `Theme.Style.HAND`; сигнатуры конструкторов не меняются.

- [ ] **Step 1: Создать `Ink.java`**

Только статические методы и приватный кэш `Map<String, BufferedImage>`. Никакого состояния окна. Эрозия: текст рисуется в маску, маска умножается на детерминированный шум, результат кэшируется.

- [ ] **Step 2: Ветка `Card`**

Для `HAND`: светлая бумага, тень `#A7A395` со смещением 2 px, рваный нижний край, рамка `#1C1B18` 1 px; без скруглений, без заклёпок. Кэшировать фон карточки по размеру.

- [ ] **Step 3: Ветки `Btn`**

PRIMARY: заливка `brass`, текст `on.brass` трафаретом, рамка от руки, при hover — `brass.hover` и сдвиг оттиска на 1 px, при press — сдвиг вниз. GHOST: прозрачный, чернильная рамка, hover — штриховка. WINDOW/CLOSE: чернильные глифы с бумажным ореолом; CLOSE при hover — инверсия.

- [ ] **Step 4: Ветка `Field`**

Без рамки: нижняя линия `ink` 1 px, в фокусе — `brass` 2 px. Каретка и выделение — латунь. Плейсхолдер — `muted`, 12 px.

- [ ] **Step 5: Собрать и проверить визуально**

Run: `.\build.ps1`, затем `java -Delium.dir="$env:TEMP\eger-ui" -jar build\EliumLauncher.jar`. Expected: бланк с рваным краем, латунная кнопка, поле-линия; наведение и фокус видимы.

- [ ] **Step 6: Коммит**

```powershell
git add src/com/elium/launcher/Ink.java src/com/elium/launcher/UI.java
git commit -m "feat: чернильные карточка, кнопки и поле"
```

---

### Task 5: Остальные контролы и выпадающий список

**Files:**
- Modify: `src/com/elium/launcher/UI.java:330-613`
- Modify: `src/com/elium/launcher/Ink.java` (при необходимости)

**Interfaces:**
- Produces: `UI.Progress`, `UI.Pill`, `UI.Steps`, `UI.Badge`, `UI.Toggle`, `UI.Slider` с ветками `HAND`.
- Produces: `UI.Select(Theme t, String[] labels, String[] values, String value, Consumer<String> onChange)`; `String value()`; раскрытый список — `JWindow` с бумажной карточкой, стрелки/Enter/Escape.

- [ ] **Step 1: `Progress`**

Чернильная рамка, латунная заливка с рваным передним краем, остаток — косая штриховка. Индетерминированный режим — движущийся латунный сегмент.

- [ ] **Step 2: `Pill`**

Узкая рамка от руки, точка `online`/`offline`, текст 13 px. Пульсация точки только когда `online`, таймер 1.8 с.

- [ ] **Step 3: `Steps`**

Римские номера I–VI, текст машинописный 14 px, высота строки 26. DONE — чернильная галочка-оттиск; ACTIVE — латунная орбитальная точка; PENDING — бледная точка.

- [ ] **Step 4: `Badge`**

Повёрнутая на −4° латунная печать с двойной рамкой, заглавные, 11 px.

- [ ] **Step 5: `Toggle` и `Slider`**

Toggle: чернильный квадрат 22×22, при включении — латунная заливка и галочка-оттиск. Slider: чернильная линия с рисками, латунная заливка, шайба с насечкой; шаг и `IntConsumer` не меняются.

- [ ] **Step 6: `Select`**

Закрытое поле: бумага, чернильная рамка, значение и треугольник. Popup: `JWindow` без декора, бумажная карточка, строки 32 px, выбранная — латунная. Клавиатура: Up/Down/Enter/Escape; клик вне — закрыть.

- [ ] **Step 7: Собрать и проверить**

Run: `.\build.ps1`; открыть настройки, подвигать слайдеры, переключить тумблеры, открыть список. Expected: все элементы в одном стиле, список управляется клавиатурой.

- [ ] **Step 8: Коммит**

```powershell
git add src/com/elium/launcher/UI.java src/com/elium/launcher/Ink.java
git commit -m "feat: чернильные прогресс, шаги, тумблеры и список"
```

---

### Task 6: Главный экран — плакат, тексты, иконка

**Files:**
- Modify: `src/com/elium/launcher/UI.java:76-124` (`Backdrop`)
- Modify: `src/com/elium/launcher/LauncherApp.java:28-250, 611-625`

**Interfaces:**
- Produces: `UI.Backdrop` для `HAND` рисует бумагу + иллюстрацию multiply + винтетку; фото-фон игнорируется только в `HAND`.
- Produces: раскладка: «ЕГЕРЬ» x=44, y≈58, кегль 104; линейка y≈178; подзаголовки y≈190/208; статус y≈230; бланк x=44, y=272, 440×236; ссылки y=514; иллюстрация x≈470…920.
- Produces: `LauncherApp.icon(int size)` берёт `t.handIcon` для `HAND`, иначе `t.icon`.
- Produces: тексты из спеки.

- [ ] **Step 1: `Backdrop` для `HAND`**

Бумажная база из `handPaper` (cover/tile), зерно, пятна, винтетка, чертёжная сетка 2 %, иллюстрация справа с multiply и градиентной маской слева. Кэш по размеру окна.

- [ ] **Step 2: Перекомпоновать `show()`**

Перенести бланк влево под слово, иллюстрацию оставить справа. Слово «ЕГЕРЬ» рисовать `Ink.inkText` шрифтом `t.font(Font.BOLD, 104f)`, а не `logo.png`. Подзаголовки: «НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939» и «ОПЫТНАЯ ДЕГУСТАЦИОННАЯ СТАНЦИЯ». Кнопки окна поверх иллюстрации с бумажным ореолом.

- [ ] **Step 3: Переписать бланк входа**

Заголовок «ДЕГУСТАЦИЯ МАЙОНЕЗА» 22 px; печать «ОПЫТНАЯ ПАРТИЯ»; подсказка «Позывной дегустатора: латиница, цифры и _ (3–16)»; поле 392×46; кнопка «НА ДЕГУСТАЦИЮ» 330×54 + квадрат настроек 54×54; статус памяти; версия «Лаунчер 0.3.0 · опытная партия».

- [ ] **Step 4: Обновить тексты статусов и ошибок**

`pingServer()`: «Приёмка открыта · N/M дегустаторов» / «Приёмка закрыта — сервер не отвечает». Ошибка позывного: «Неверный позывной: 3–16 символов, A–Z, 0–9, _». Заголовок окна: «Егерь (опытная партия 0.3.0)».

- [ ] **Step 5: Иконка окна**

`icon(int)` возвращает `t.handIcon` при `HAND`, иначе `t.icon`. Убедиться, что `frame.setIconImages` собирает 16/32/64 из нужного набора.

- [ ] **Step 6: Проверить визуально**

Run: `.\build.ps1`, `java -Delium.dir="$env:TEMP\eger-main" -jar build\EliumLauncher.jar`. Expected: слева «ЕГЕРЬ», под ним бланк, справа рука с банкой; иллюстрация не перекрывает текст; фокус и hover работают.

- [ ] **Step 7: Коммит**

```powershell
git add src/com/elium/launcher/UI.java src/com/elium/launcher/LauncherApp.java
git commit -m "feat: плакатный главный экран и тексты 1939"
```

---

### Task 7: Экран загрузки и «ДОНЕСЕНИЕ»

**Files:**
- Modify: `src/com/elium/launcher/LauncherApp.java:214-250, 463-530, 606-609`
- Modify: `src/com/elium/launcher/UI.java` (добавить `UI.message`)

**Interfaces:**
- Produces: бланк загрузки x=44, y=224, 440×316; шаги 26 px; заголовок «ПРИЁМКА».
- Produces: `static void UI.message(Window owner, Theme t, String title, String text, boolean error)` — модальный `JDialog`, бумажный лист, ширина 520, высота 260–640, `JTextArea` с переносом и прокруткой, кнопка «ПОНЯТНО».
- Consumes: `Theme`, `Ink` из Task 4–5.

- [ ] **Step 1: Перекомпоновать бланк загрузки**

Заголовок «ПРИЁМКА», шаги, строка действия, файл, прогресс, объём/скорость/остаток. Тексты: «Партия принята — Minecraft открывается», «Ошибка — подробности в донесении».

- [ ] **Step 2: Реализовать `UI.message`**

Только `getMessage()`; `JTextArea` `lineWrap=true`, `wrapStyleWord=true`, `editable=false`, `opaque=false`; `JScrollPane` без рамки; высота = clamp(260, текст+кнопка, 640). Оформление — бумага, чернильная рамка, инверсная печать «ОШИБКА»/«ДОНЕСЕНИЕ».

- [ ] **Step 3: Заменить `error(Exception)`**

Вызывать `UI.message(frame, t, "ДОНЕСЕНИЕ", text, true)`; стартовое исключение в `main()` оставить `JOptionPane`.

- [ ] **Step 4: Проверить длинную ошибку**

Временно указать в настройках неверный Modpack URL (например `http://127.0.0.1:1/manifest.json`), нажать «НА ДЕГУСТАЦИЮ», дождаться ошибки. Expected: окно не выше 640, текст переносится и прокручивается, кнопка видна.

- [ ] **Step 5: Коммит**

```powershell
git add src/com/elium/launcher/LauncherApp.java src/com/elium/launcher/UI.java
git commit -m "feat: экран приёмки и донесение об ошибке"
```

---

### Task 8: Настройки

**Files:**
- Modify: `src/com/elium/launcher/LauncherApp.java:252-409`

**Interfaces:**
- Produces: окно 760×620, две колонки 328 px, заголовок «НАСТРОЙКИ», подпись «СЛУЖЕБНАЯ ЧАСТЬ · ОПЫТНАЯ ПАРТИЯ».
- Produces: `UI.Select` для оформления, значения `hand|clean|military|sketch`, подписи `Ручная работа|Чистый|Военный|Набросок`, подсказка «применится после перезапуска».
- Produces: `Config.saveUserSettings(...)` без `customModsDir` (Task 1).

- [ ] **Step 1: Перекомпоновать левую колонку**

RAM-слайдер, автоподключение, потоки, автообновление, логи. Отступы и высоты — по спеке; ничего не обрезать.

- [ ] **Step 2: Перекомпоновать правую колонку**

Список оформления, Modpack URL, JVM-аргументы, сервер host/port, «Открыть папку игры». Блока custom-модов и админ-панели нет.

- [ ] **Step 3: Подключить `UI.Select` и сохранение**

При «Сохранить» передавать сырое значение (`hand` и т.д.) в `saveUserSettings`; обновлять `ramMb`, `autoConnect`, потоки. Подсказка о перезапуске.

- [ ] **Step 4: Проверить**

Run: открыть настройки, изменить RAM и потоки, выбрать «Военный», сохранить, перезапустить. Expected: значения сохранились, стиль применился после перезапуска, ошибок нет.

- [ ] **Step 5: Коммит**

```powershell
git add src/com/elium/launcher/LauncherApp.java
git commit -m "feat: настройки в ручном стиле"
```

---

### Task 9: Сборка, версия и ассеты в jar

**Files:**
- Modify: `build.ps1:18-25`
- Modify: `src/com/elium/launcher/LauncherApp.java:31`
- Modify: `src/com/elium/launcher/theme.properties` (если ключи ещё не финальны)

**Interfaces:**
- Produces: `build\EliumLauncher.jar` содержит `theme.properties`, `launcher.properties`, `icon.png`, `hand-hero.png`, `paper.png`, `hand-icon.png`, `fonts/*`.
- Produces: `LauncherApp.VERSION = "0.3.0"`.
- Produces: `build.ps1` копирует `theme\*` в `build\classes` рекурсивно перед `jar`.

- [ ] **Step 1: Обновить `build.ps1`**

После копирования `icon.png` добавить рекурсивное копирование `theme\*` в `$out\classes\`. Убедиться, что `jpackage` по-прежнему копирует `theme\*` рядом с exe и использует обновлённый `icon.ico`.

- [ ] **Step 2: Поднять версию**

`VERSION = "0.3.0"`.

- [ ] **Step 3: Проверить содержимое jar**

```powershell
.\build.ps1
jar tf build\EliumLauncher.jar | Select-String "hand-hero|paper.png|hand-icon|fonts/|theme.properties"
```

Expected: все перечисленные записи найдены.

- [ ] **Step 4: Запуск только из jar**

Скопировать `build\EliumLauncher.jar` во временную папку без `theme/`, запустить `java -Delium.dir="$env:TEMP\eger-jar" -jar <temp>\EliumLauncher.jar`. Expected: полный вид с иллюстрацией и шрифтами.

- [ ] **Step 5: Собрать exe**

```powershell
.\build.ps1 -Installer
```

Expected: `release\Eger-0.3.0-test.exe` создан, иконка новая.

- [ ] **Step 6: Коммит**

```powershell
git add build.ps1 src/com/elium/launcher/LauncherApp.java src/com/elium/launcher/theme.properties
git commit -m "build: 0.3.0 и ассеты внутри jar"
```

---

### Task 10: Полная проверка

**Files:**
- Modify: только найденные дефекты.

**Interfaces:**
- Consumes: все предыдущие задачи.

- [ ] **Step 1: Пройти чек-лист спеки**

Проверить пункты 1–15 раздела 13: чистый профиль, старый профиль, вход, пинг, настройки, полный запуск, ошибка, четыре стиля, масштабы, custom-моды, git diff, иконка, jar, релиз (релиз — Task 11).

- [ ] **Step 2: Масштабы**

Windows 100 %, 125 %, 150 %: окно и настройки без обрезки. При обрезке заменить жёсткие координаты на пересчёт от `w/h` в проблемном месте.

- [ ] **Step 3: Старые стили**

Переключить `clean`, `military`, `sketch`: окно открывается, функции работают. «Военный» остаётся тёмным.

- [ ] **Step 4: Битые ассеты**

Переименовать `hand-hero.png` и `RussoOne-Regular.ttf` во внешней папке; запустить. Expected: бумажный фон, системный шрифт, stderr с причиной, без падения.

- [ ] **Step 5: Проверить незакоммиченные правки**

```powershell
git diff --stat
git status --short
```

Expected: изменения Linux/macOS на месте; в коммитах нет `GameInstaller.java`, `GameLauncher.java`, `JavaRuntime.java`, `SelfUpdate.java`, `build.sh` без явного решения.

- [ ] **Step 6: Коммит исправлений**

```powershell
git add <исправленные файлы>
git commit -m "fix: замечания проверки 0.3.0"
```

---

### Task 11: Публикация 0.3.0 и проверка автообновления

**Files:**
- Modify: нет, если проверки прошли.

**Interfaces:**
- Consumes: `build.ps1 -Publish`, `SelfUpdate` (не менять).
- Produces: GitHub-релиз `v0.3.0-<sha7>` с `EliumLauncher.jar`, `Eger-0.3.0-test.exe`, телом `sha1: <hex>`, `--latest`.

- [ ] **Step 1: Убедиться в готовности**

```powershell
Select-String src\com\elium\launcher\LauncherApp.java -Pattern 'VERSION = "0.3.0"'
gh auth status
```

Expected: версия 0.3.0, gh авторизован под `exxtezys`.

- [ ] **Step 2: Опубликовать**

```powershell
.\build.ps1 -Publish
```

Expected: команда завершается без ошибок, печатает `опубликован v0.3.0-...`.

- [ ] **Step 3: Проверить релиз**

```powershell
gh release view --repo exxtezys/eger-launcher --json tagName,isLatest,assets,body
```

Expected: `isLatest=true`, ассеты `EliumLauncher.jar` и `Eger-0.3.0-test.exe`, в body строка `sha1:` и она совпадает с `(Get-FileHash build\EliumLauncher.jar -Algorithm SHA1).Hash`.

- [ ] **Step 4: Проверить автообновление на копии 0.2.0**

```powershell
$t = "$env:TEMP\eger-update-test"; Remove-Item -Recurse -Force $t -ErrorAction SilentlyContinue; New-Item -ItemType Directory $t | Out-Null
gh release download v0.2.0-92bec6e --repo exxtezys/eger-launcher --pattern EliumLauncher.jar --dir $t
java -Delium.dir="$t\data" -Delium.update.github=exxtezys/eger-launcher -jar "$t\EliumLauncher.jar"
```

Expected: лаунчер скачивает 0.3.0, заменяет `$t\EliumLauncher.jar`, открывает новое окно; SHA1 файла в `$t` совпадает с релизом; окно в стиле `hand`. Закрыть окно, процесс завершить.

- [ ] **Step 5: Отчёт**

Сообщить владельцу: тег, SHA1, ссылку на релиз, результат теста автообновления. При ошибке удалить релиз и вернуть `latest` на 0.2.0.

---

## Self-Review

- **Spec coverage:** удаление модов — Task 1; палитра/тема/ревизия/миграция — Task 2; ассеты, иконка, шрифты — Task 3; компоненты — Task 4–5; главный экран и тексты — Task 6; загрузка и ошибки — Task 7; настройки и список — Task 8; сборка/версия/jar — Task 9; проверка — Task 10; публикация и автообновление — Task 11.
- **Step scan:** каждый шаг даёт одно проверяемое действие; сигнатуры и значения зафиксированы, тела не переписаны.
- **Type consistency:** `Config.saveUserSettings` без `customModsDir` используется в Task 8; `UI.Select` из Task 5 используется в Task 8; `UI.message` из Task 7 используется в Task 10; `Theme.handIcon` из Task 2 используется в Task 6.
- **Review Focus:** пункты 1–5 привязаны к Task 2, 9, 7, 10, 3/4; автообновление — Task 11.
- **Proportion:** план фиксирует решения и проверки, не переписывает реализацию.
