# Зеркала загрузки — план реализации

> **Для агентов:** ОБЯЗАТЕЛЬНЫЙ ПОД-НАВЫК: используйте superpowers:subagent-driven-development (рекомендуется) или superpowers:executing-plans, чтобы выполнять план задача за задачей. Шаги размечены чекбоксами (`- [ ]`).

**Цель:** игрок из России запускает лаунчер, и Minecraft + NeoForge + Java скачиваются до конца без VPN и без каких-либо действий с его стороны.

**Архитектура:** новый класс `Mirrors` хранит для каждого хоста список кандидатов и правило подстановки пути. Одна разведка в начале установки выбирает рабочий источник для каждой группы хостов и кеширует выбор. `Net.download` при неудаче перебирает кандидатов вместо повторов по одному адресу. Библиотеки NeoForge лаунчер качает сам (из `install_profile.json` установщика), после чего установщик работает как офлайн-сборщик.

**Стек:** Java 21, только стандартная библиотека, `javac`/`jar` из `build.ps1`. Тестового фреймворка в проекте нет — тесты пишутся как классы с `main`, запускаются `java -cp`.

**Спека:** `docs/superpowers/specs/2026-11-07-download-mirrors-design.md`

## Глобальные ограничения

- Только стандартная библиотека Java, никаких новых зависимостей.
- Сборка: `.\build.ps1` (JDK в `C:\Program Files\Java\jdk-21\bin`).
- Незакоммиченные правки в `Config.java`, `GameInstaller.java`, `Net.java`, `JavaRuntime.java`, `SelfUpdate.java` под Linux/macOS **не терять**.
- Прокси (`ProxyNet`) имеет приоритет над зеркалами: если прокси включён, зеркала не используются.
- sha1 обязателен к проверке там, где он известен.
- Адреса зеркал — только проверенные, из спеки. Не выдумывать новых.

## Фокус ревью

Входы и состояния, которые спека подразумевает, но ни один тест задачи не покрывает напрямую:

1. Прокси включён игроком — зеркала не должны применяться, чтобы не сломать рабочую настройку.
2. Зеркало ответило 200, но файл битый (несовпадение sha1) — зеркало исключается до конца сессии, а не переиспользуется на каждом файле.
3. Все источники недоступны — сообщение называет шаг и не содержит голого текста исключения.
4. Установщик NeoForge запускается при уже готовых библиотеках и не ходит на `maven.neoforged.net`.
5. Разведка при полностью недоступной сети — не зависает дольше нескольких секунд на группу.

---

### Задача 1: Класс `Mirrors` — правила подстановки

**Файлы:**
- Создать: `src/com/elium/launcher/Mirrors.java`
- Создать: `src/test/MirrorsTest.java`

**Интерфейсы:**
- `Mirrors.alternatives(String url)` → `List<String>`: для официального URL возвращает кандидатов-зеркал по порядку, **не включая** сам оригинал. Для неизвестного URL — пустой список.
- `Mirrors.isOfficial(String url)` → `boolean`.

- [ ] **Шаг 1: Написать падающий тест**

`src/test/MirrorsTest.java`, класс с `main`, проверяет подстановки из спеки:

```java
package test;

import com.elium.launcher.Mirrors;
import java.util.List;

public class MirrorsTest {
    private static int failed = 0;

    static void eq(String what, Object expected, Object actual) {
        if (!java.util.Objects.equals(expected, actual)) {
            System.out.println("FAIL " + what + ": ожидалось " + expected + ", получено " + actual);
            failed++;
        }
    }

    public static void main(String[] args) {
        eq("manifest", List.of("https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json"),
                Mirrors.alternatives("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"));

        eq("neo maven", List.of(
                        "https://bmclapi2.bangbang93.com/maven/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar",
                        "https://maven.creeperhost.net/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar"),
                Mirrors.alternatives("https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar"));

        eq("libraries", List.of("https://bmclapi2.bangbang93.com/libraries/com/mojang/logging/1.5.10/logging-1.5.10.jar"),
                Mirrors.alternatives("https://libraries.minecraft.net/com/mojang/logging/1.5.10/logging-1.5.10.jar"));

        eq("assets", List.of("https://bmclapi2.bangbang93.com/assets/ab/cdef"),
                Mirrors.alternatives("https://resources.download.minecraft.net/ab/cdef"));

        eq("piston-data", List.of("https://bmclapi2.bangbang93.com/version/1.21.1/client"),
                Mirrors.alternatives("https://piston-data.mojang.com/v1/objects/30c73b1c5da787909b2f73340419fdf13b9def88/client.jar"));

        eq("github api", List.of("https://gh-proxy.com/https://api.github.com/repos/a/b/releases/latest"),
                Mirrors.alternatives("https://api.github.com/repos/a/b/releases/latest"));

        eq("неизвестный", List.of(), Mirrors.alternatives("https://example.com/x"));

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
    }
}
```

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `C:\Program Files\Java\jdk-21\bin\javac.exe -encoding UTF-8 -d C:\Users\User\AppData\Local\Temp\eger-t src\com\elium\launcher\Mirrors.java src\test\MirrorsTest.java`
Expected: ошибка компиляции — `Mirrors` не существует.

- [ ] **Шаг 3: Реализовать `Mirrors`**

Правило подстановки — префикс оригинального URL → префикс зеркала. Порядок кандидатов: BMCLAPI первым (проверено рабочим), Creeperhost вторым. Для `piston-data` путь не переносится как есть: BMCLAPI отдаёт клиент по `/version/<mc>/client`, поэтому подстановка строится на `version` из имени файла — если распознать не удалось, вернуть пустой список (лучше не использовать зеркало, чем скачать мусор).

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: тот же `javac`, затем `java -cp C:\Users\User\AppData\Local\Temp\eger-t test.MirrorsTest`
Expected: `OK`

- [ ] **Шаг 5: Коммит**

```bash
git add src/com/elium/launcher/Mirrors.java src/test/MirrorsTest.java
git commit -m "feat: правила зеркал для загрузок"
```

---

### Задача 2: Перебор кандидатов в `Net.download`

**Файлы:**
- Изменить: `src/com/elium/launcher/Net.java:102-145`
- Создать: `src/test/NetFallbackTest.java`

**Интерфейсы:**
- Потребляет: `Mirrors.alternatives(String)` из задачи 1.
- Производит: `Net.download(Task, Counter)` — поведение меняется, сигнатура нет. Добавляется `Net.setMirrorsEnabled(boolean)`.

- [ ] **Шаг 1: Написать падающий тест**

Тест поднимает `com.sun.net.httpserver.HttpServer` на 127.0.0.1 со случайным портом. Первый обработчик отвечает 500, второй — корректными байтами. Задача с URL, для которого `Mirrors.alternatives` возвращает второй адрес, должна скачаться успешно.

```java
// ключевые проверки:
// 1. файл существует и содержимое совпадает с ожидаемым
// 2. сервер-отказник получил ровно 1 запрос (без трёх повторов)
// 3. при полном отказе всех — IOException с текстом про источники
```

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `java -cp ... test.NetFallbackTest`
Expected: FAIL — скачивание бросает исключение, файла нет.

- [ ] **Шаг 3: Реализовать перебор**

В `download` внешний цикл по кандидатам: оригинал, затем `Mirrors.alternatives(url)`. Внутри — одна попытка на кандидата с одним повтором. При исчерпании всех — `IOException` с перечнем опробованных источников. Несовпадение sha1 → кандидат помечается плохим на сессию (`Net` хранит `Set<String>` битых зеркал подстановки) и сразу идёт следующий; к этому кандидату больше не обращаемся.

Если `Config.proxyOn()` — `setMirrorsEnabled(false)`, перебор выключен (фокус ревью 1).

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: `java -cp ... test.NetFallbackTest`
Expected: `OK`

- [ ] **Шаг 5: Коммит**

```bash
git add src/com/elium/launcher/Net.java src/test/NetFallbackTest.java
git commit -m "feat: перебор зеркал при неудачной загрузке"
```

---

### Задача 3: Разведка хостов один раз за сессию

**Файлы:**
- Создать: `src/com/elium/launcher/Probe.java`
- Изменить: `src/com/elium/launcher/Net.java`
- Создать: `src/test/ProbeTest.java`

**Интерфейсы:**
- Производит: `Probe.choose(boolean mirrorsEnabled)` → `void`, заполняет у `Mirrors` предпочтительный индекс для каждой группы хостов, кеширует в `<gameDir>/mirror-choice.properties`.
- Потребляет: `Mirrors` (задача 1).

- [ ] **Шаг 1: Написать падающий тест**

Два локальных HTTP-сервера: «официальный» отвечает с задержкой 3000 мс, «зеркальный» — сразу. После `Probe.choose(true)` группа должна указывать на зеркало. Второй случай: оба отвечают быстро — выбирается официальный. Третий: оба молчат — выбор не падает с исключением, остаются оригиналы.

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `java -cp ... test.ProbeTest`
Expected: FAIL — `Probe` не существует.

- [ ] **Шаг 3: Реализовать `Probe`**

Параллельный `HEAD` на каждый кандидат каждой группы, таймаут 5 секунд на запрос, общий потолок — 8 секунд на всю разведку. Побеждает первый ответивший `2xx`; при равенстве предпочитается оригинал. Результат пишется в `mirror-choice.properties` и читается при следующем старте; файл перечитывается заново, если сохранённый выбор ведёт к отказам.

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: `java -cp ... test.ProbeTest`
Expected: `OK`

- [ ] **Шаг 5: Коммит**

```bash
git add src/com/elium/launcher/Probe.java src/com/elium/launcher/Net.java src/test/ProbeTest.java
git commit -m "feat: разведка доступных источников загрузки"
```

---

### Задача 4: Библиотеки NeoForge качаем сами

**Файлы:**
- Изменить: `src/com/elium/launcher/GameInstaller.java:111-141`
- Создать: `src/test/InstallerLibsTest.java`

**Интерфейсы:**
- Производит: `GameInstaller.seedInstallerLibraries(Path installerJar, Path gameDir, Net.Progress p)` → `int` (число скачанных библиотек).
- Потребляет: `Net.downloadAll`, `Mirrors`.

- [ ] **Шаг 1: Написать падающий тест**

Скачать установщик из временного каталога (он уже там: `C:\Users\User\AppData\Local\Temp\opencode\neo-inst\neoforge-installer.jar`). Вызвать `seedInstallerLibraries`, проверить, что в `<gameDir>/libraries` появились `net/neoforged/fancymodloader/loader/4.0.44/loader-4.0.44.jar` и `net/neoforged/installertools/installertools/2.1.2/installertools-2.1.2.jar`, и что число больше 60.

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `java -cp ... test.InstallerLibsTest`
Expected: FAIL — метода нет.

- [ ] **Шаг 3: Реализовать**

Открыть установщик как zip (`ZipFile`), прочитать `install_profile.json`, взять `libraries[].downloads.artifact` (`url`, `path`, `sha1`, `size`), собрать `Net.Task` на `<gameDir>/libraries/<path>`, скачать через `Net.downloadAll`. Вызвать **до** `runNeoInstaller` в `install()` (перед строкой 48). Установщику **не** передавать `--mirror` — бесполезен.

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: `java -cp ... test.InstallerLibsTest`
Expected: `OK`

- [ ] **Шаг 5: Проверить, что установщик не ходит на maven.neoforged.net**

Запустить установку в чистый каталог с уже засеянными библиотеками и пустым `versions/`, затем прочитать `neoforge-installer.jar.log`.
Expected: в логе нет `Downloading library from https://maven.neoforged.net`, процесс завершается с кодом 0 и создаёт `versions/neoforge-21.1.252/neoforge-21.1.252.json`.

- [ ] **Шаг 6: Коммит**

```bash
git add src/com/elium/launcher/GameInstaller.java src/test/InstallerLibsTest.java
git commit -m "feat: библиотеки NeoForge качаются через зеркала до запуска установщика"
```

---

### Задача 5: Java с зеркала

**Файлы:**
- Изменить: `src/com/elium/launcher/JavaRuntime.java:13-20`
- Изменить: `src/launcher.properties`
- Изменить: `src/com/elium/launcher/Config.java` (поле `javaVersion`)
- Создать: `src/test/JavaUrlTest.java`

**Интерфейсы:**
- Производит: `Config.javaVersion` → `String` (например `21.0.13_9`), `JavaRuntime.mirrorUrls(String version, String os, String arch)` → `List<String>`.

- [ ] **Шаг 1: Написать падающий тест**

```java
// для version=21.0.13_9, os=windows, arch=x64 ожидается первый адрес:
// https://mirrors.tuna.tsinghua.edu.cn/Adoptium/21/jre/x64/windows/OpenJDK21U-jre_x64_windows_hotspot_21.0.13_9.zip
// и второй — gh-proxy на релиз adoptium/temurin21-binaries
```

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `java -cp ... test.JavaUrlTest`
Expected: FAIL.

- [ ] **Шаг 3: Реализовать**

Добавить `java.version=21.0.13_9` в `launcher.properties`, поле в `Config`. В `JavaRuntime` официальный URL оставить первым, зеркала — после. Пропускать зеркало, если для пары os/arch формула имени файла неизвестна.

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: `java -cp ... test.JavaUrlTest`
Expected: `OK`

- [ ] **Шаг 5: Проверить реальным скачиванием**

Скачать по построенному зеркальному URL, распаковать, найти `bin/javaw.exe`.
Expected: файл существует.

- [ ] **Шаг 6: Коммит**

```bash
git add src/com/elium/launcher/JavaRuntime.java src/com/elium/launcher/Config.java src/launcher.properties src/test/JavaUrlTest.java
git commit -m "feat: зеркало для загрузки Java 21"
```

---

### Задача 6: Обновление лаунчера через прокси-зеркало

**Файлы:**
- Изменить: `src/com/elium/launcher/SelfUpdate.java:39-58`

**Интерфейсы:**
- Потребляет: `Net.download` с перебором (задача 2), `Mirrors.alternatives`.

- [ ] **Шаг 1: Проверить, что тест задачи 1 покрывает правило**

`Mirrors.alternatives("https://api.github.com/...")` уже возвращает `gh-proxy.com`-адрес (задача 1, шаг 4). Отдельный тест не нужен.

- [ ] **Шаг 2: Убедиться, что `SelfUpdate` использует перебор**

`Net.download` в строке 52 уже пойдёт через перебор после задачи 2. Проверить, что `Net.getText` в строке 41 тоже умеет зеркала — если нет, добавить в `getText` тот же перебор.

- [ ] **Шаг 3: Проверить реальным запросом**

Run: `curl.exe -s -o NUL -w "%{http_code}" -L "https://gh-proxy.com/https://api.github.com/repos/exxtezys/eger-launcher/releases/latest"`
Expected: `200`

- [ ] **Шаг 4: Коммит**

```bash
git add src/com/elium/launcher/SelfUpdate.java src/com/elium/launcher/Net.java
git commit -m "feat: обновление лаунчера через зеркало"
```

---

### Задача 7: Понятная ошибка вместо технической строки

**Файлы:**
- Изменить: `src/com/elium/launcher/LauncherApp.java:876-878`
- Изменить: `src/com/elium/launcher/Net.java` (тексты исключений)

- [ ] **Шаг 1: Написать падающий тест**

Проверить, что `Net.download` при отказе всех источников бросает `IOException`, в сообщении которого есть название шага и слово «прокси», и нет подстроки `java.net.`.

- [ ] **Шаг 2: Убедиться, что тест падает**

Run: `java -cp ... test.ErrorTextTest`
Expected: FAIL.

- [ ] **Шаг 3: Реализовать**

Ввести `Net.HostsUnavailableException extends IOException` с полем «шаг». В `LauncherApp.error` для этого типа показывать текст: что не скачалось, что все источники перебраны, строка «Проверьте прокси в настройках» и «Повторить». Остальные исключения — как сейчас. Подробности (список опробованных URL) — в `System.err`.

- [ ] **Шаг 4: Убедиться, что тест проходит**

Run: `java -cp ... test.ErrorTextTest`
Expected: `OK`

- [ ] **Шаг 5: Собрать и проверить вручную**

Run: `.\build.ps1`
Expected: `OK: build\EliumLauncher.jar`, запуск лаунчера без ошибок.

- [ ] **Шаг 6: Коммит**

```bash
git add src/com/elium/launcher/Net.java src/com/elium/launcher/LauncherApp.java
git commit -m "feat: понятное сообщение при недоступности всех источников"
```
