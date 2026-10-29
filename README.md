# Егерь — лаунчер

Лаунчер Minecraft 1.21.1 + NeoForge для фронтового сервера `khorn.tralala.club`.

## Для игроков

Скачайте `Eger-*-test.exe` из [последнего релиза](../../releases/latest) и запустите. Установка не нужна:
лаунчер сам скачает Java, Minecraft, NeoForge и моды сервера, а при новых релизах обновится сам.

## Сборка

Нужны JDK 21 (`C:\Program Files\Java\jdk-21`) и Windows (.NET Framework 4 для exe).

```powershell
.\build.ps1            # build\EliumLauncher.jar
.\build.ps1 -Exe       # + dist\EgerLauncher\ (лаунчер со встроенной Java)
.\build.ps1 -Installer # + release\Eger-<версия>-test.exe — один файл для раздачи
.\build.ps1 -Publish   # + релиз на GitHub: все лаунчеры обновятся при следующем запуске
```

Перед `-Publish` поднимите версию в `LauncherApp.VERSION`.

Настройки сервера, папки игры и репозитория обновлений — `src/launcher.properties`.
Оформление — `src/theme.properties` и картинки в `theme/` (генерируются `tools/make_theme.py`).
