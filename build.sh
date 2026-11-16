#!/usr/bin/env bash
set -euo pipefail

APPIMAGE=0
INSTALLER=0
PUBLISH=0

for arg in "$@"; do
    case "$arg" in
        --appimage) APPIMAGE=1 ;;
        --installer) INSTALLER=1 ;;
        --publish) PUBLISH=1 ;;
    esac
done

if [ "$PUBLISH" -eq 1 ]; then INSTALLER=1; fi
if [ "$INSTALLER" -eq 1 ]; then APPIMAGE=1; fi

JDK="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk}"
JAVAC="$JDK/bin/javac"
JAR="$JDK/bin/jar"
JPACKAGE="$JDK/bin/jpackage"

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/build"
VERSION=$(grep -o 'VERSION = "[^"]*"' "$ROOT/src/com/elium/launcher/LauncherApp.java" | sed 's/VERSION = "//;s/"//')

rm -rf "$OUT"
mkdir -p "$OUT/classes"

# compile
find "$ROOT/src" -name '*.java' -print0 | xargs -0 "$JAVAC" --release 21 -encoding UTF-8 -d "$OUT/classes"

cp "$ROOT/src/launcher.properties" "$ROOT/src/theme.properties" "$OUT/classes/"
if [ -f "$ROOT/theme/icon.png" ]; then cp "$ROOT/theme/icon.png" "$OUT/classes/"; fi

"$JAR" --create --file "$OUT/EliumLauncher.jar" --main-class com.elium.launcher.LauncherApp -C "$OUT/classes" .
echo "OK: $OUT/EliumLauncher.jar (version $VERSION)"

if [ "$APPIMAGE" -eq 1 ]; then
    DIST="$ROOT/dist"
    rm -rf "$DIST"
    mkdir -p "$OUT/in"
    cp "$OUT/EliumLauncher.jar" "$OUT/in/"
    ICON_ARGS=()
    if [ -f "$ROOT/icon.png" ]; then ICON_ARGS=(--icon "$ROOT/icon.png"); fi
    "$JPACKAGE" --type app-image --name EgerLauncher --input "$OUT/in" \
        --main-jar EliumLauncher.jar --main-class com.elium.launcher.LauncherApp \
        --app-version "${VERSION//[^0-9.]/}" --vendor 'Eger' \
        --description 'Eger Launcher (test)' "${ICON_ARGS[@]}" \
        --add-modules java.base,java.desktop,java.net.http,java.management,jdk.management,jdk.crypto.ec,jdk.zipfs \
        --jlink-options '--strip-debug --no-header-files --no-man-pages' \
        --dest "$DIST"
    cp "$ROOT/src/theme.properties" "$DIST/EgerLauncher/"
    if [ -d "$ROOT/theme" ]; then cp -r "$ROOT/theme/"* "$DIST/EgerLauncher/"; fi
    echo "OK: $DIST/EgerLauncher/EgerLauncher"
fi

if [ "$INSTALLER" -eq 1 ]; then
    RELEASE="$ROOT/release"
    rm -rf "$RELEASE"
    mkdir -p "$RELEASE" "$OUT/stub"
    (cd "$DIST/EgerLauncher" && tar -czf "$OUT/stub/app.tar.gz" .)
    BUILD="$VERSION-$(sha1sum "$OUT/stub/app.tar.gz" | cut -c1-10)"
    sed "s/__BUILD__/$BUILD/g" "$ROOT/tools/stub/EgerStub.sh" > "$OUT/stub/EgerStub.sh"
    chmod +x "$OUT/stub/EgerStub.sh"
    cat "$OUT/stub/EgerStub.sh" "$OUT/stub/app.tar.gz" > "$RELEASE/Eger-$VERSION-linux.tar.gz"
    chmod +x "$RELEASE/Eger-$VERSION-linux.tar.gz"
    echo "OK: $RELEASE/Eger-$VERSION-linux.tar.gz (build $BUILD)"
fi
