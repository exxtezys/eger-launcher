#!/usr/bin/env bash
# Самораспаковывающийся стаб для Linux/macOS: распаковывает себя в ~/.local/share/eger/launcher/<build>/
# и запускает EgerLauncher оттуда. Проверяет маркер .ok — если есть, не распаковывает заново.

set -euo pipefail

BUILD="__BUILD__"
ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/eger/launcher"
DIR="$ROOT/$BUILD"
EXE="$DIR/EgerLauncher"

if [ ! -f "$DIR/.ok" ]; then
    TMP="$DIR.tmp"
    rm -rf "$TMP"
    mkdir -p "$TMP"
    # Извлечь payload (всё после маркера __PAYLOAD__) из самого себя
    PAYLOAD_LINE=$(grep -a -n '^__PAYLOAD__$' "$0" | head -n1 | cut -d: -f1)
    tail -n +$((PAYLOAD_LINE + 1)) "$0" | tar -xzf - -C "$TMP"
    rm -rf "$DIR"
    mv "$TMP" "$DIR"
    printf '%s\n' "$BUILD" > "$DIR/.ok"
    # удалить старые сборки
    for old in "$ROOT"/*; do
        [ "$old" = "$DIR" ] && continue
        rm -rf "$old" 2>/dev/null || true
    done
fi

exec "$EXE" "$@"
exit 0
__PAYLOAD__
