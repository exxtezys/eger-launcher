# Сборка:
#   build.ps1            -> build\EliumLauncher.jar
#   build.ps1 -Exe       -> + dist\EgerLauncher\EgerLauncher.exe (со встроенной Java)
#   build.ps1 -Installer -> + release\Eger-<версия>-test.exe (один файл без установки, отдавать игрокам)
#   build.ps1 -Publish   -> + релиз на GitHub (update.github из launcher.properties): EliumLauncher.jar + exe,
#                           все лаунчеры игроков обновятся при следующем запуске. Версию поднимать в LauncherApp.VERSION
param([switch]$Exe, [switch]$Installer, [switch]$Publish)
$ErrorActionPreference = 'Stop'
if ($Publish) { $Installer = $true }
if ($Installer) { $Exe = $true }
$jdk = 'C:\Program Files\Java\jdk-21\bin'
$root = $PSScriptRoot
$out = Join-Path $root 'build'
$version = ([regex]::Match((Get-Content "$root\src\com\elium\launcher\LauncherApp.java" -Raw), 'VERSION = "([^"]+)"')).Groups[1].Value
Remove-Item -Recurse -Force $out -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$out\classes" | Out-Null

$src = Get-ChildItem -Recurse "$root\src" -Filter *.java | ForEach-Object FullName
& "$jdk\javac.exe" --release 21 -encoding UTF-8 -d "$out\classes" $src
if ($LASTEXITCODE -ne 0) { throw 'javac failed' }
Copy-Item "$root\src\launcher.properties","$root\src\theme.properties" "$out\classes\"
if (Test-Path "$root\theme\icon.png") { Copy-Item "$root\theme\icon.png" "$out\classes\" }
& "$jdk\jar.exe" --create --file "$out\EliumLauncher.jar" --main-class com.elium.launcher.LauncherApp -C "$out\classes" .
if ($LASTEXITCODE -ne 0) { throw 'jar failed' }
Write-Host "OK: $out\EliumLauncher.jar (version $version)"

if ($Exe) {
    $dist = Join-Path $root 'dist'
    Remove-Item -Recurse -Force $dist -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force "$out\in" | Out-Null
    Copy-Item "$out\EliumLauncher.jar" "$out\in\"
    $iconArgs = @()
    if (Test-Path "$root\icon.ico") { $iconArgs = @('--icon', "$root\icon.ico") }
    & "$jdk\jpackage.exe" --type app-image --name EgerLauncher --input "$out\in" `
        --main-jar EliumLauncher.jar --main-class com.elium.launcher.LauncherApp `
        --app-version ($version -replace '[^0-9.]', '') --vendor 'Eger' `
        --description 'Eger Launcher (test)' @iconArgs `
        --add-modules java.base,java.desktop,java.net.http,java.management,jdk.management,jdk.crypto.ec,jdk.zipfs `
        --jlink-options '--strip-debug --no-header-files --no-man-pages' `
        --dest $dist
    if ($LASTEXITCODE -ne 0) { throw 'jpackage failed' }
    # Тема и картинки рядом с exe — правятся без пересборки
    Copy-Item "$root\src\theme.properties" "$dist\EgerLauncher\"
    if (Test-Path "$root\theme") { Copy-Item "$root\theme\*" "$dist\EgerLauncher\" -Recurse }
    Write-Host "OK: $dist\EgerLauncher\EgerLauncher.exe"
}

if ($Installer) {
    # Один exe без установки: лаунчер + Java запакованы внутрь, при первом запуске распаковываются в %LOCALAPPDATA%\Eger
    Remove-Item -Recurse -Force "$root\release" -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force "$root\release", "$out\stub" | Out-Null
    $zip = "$out\stub\app.zip"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::CreateFromDirectory("$dist\EgerLauncher", $zip, [IO.Compression.CompressionLevel]::Optimal, $false)
    $build = "$version-" + (Get-FileHash $zip -Algorithm SHA1).Hash.Substring(0, 10).ToLower()
    $cs = (Get-Content "$root\tools\stub\EgerStub.cs" -Raw -Encoding UTF8).Replace('__BUILD__', $build)
    [IO.File]::WriteAllText("$out\stub\EgerStub.cs", $cs, (New-Object Text.UTF8Encoding $true))
    $fw = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319'
    $outExe = "$root\release\Eger-$version-test.exe"
    & "$fw\csc.exe" /nologo /target:winexe /optimize+ /codepage:65001 "/out:$outExe" "/win32icon:$root\icon.ico" `
        "/resource:$zip,app.zip" /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll `
        /r:System.Windows.Forms.dll "$out\stub\EgerStub.cs"
    if ($LASTEXITCODE -ne 0) { throw 'csc failed' }
    Write-Host "OK: $outExe ($([math]::Round((Get-Item $outExe).Length/1MB,1)) MB, build $build)"
}

if ($Publish) {
    $repo = (Get-Content "$root\src\launcher.properties" -Encoding UTF8 | Where-Object { $_ -match '^update\.github=' }) -replace '^update\.github=', ''
    if (-not $repo) { throw 'update.github не задан в launcher.properties' }
    $jar = "$out\EliumLauncher.jar"
    Copy-Item $jar "$root\release\EliumLauncher.jar"
    $sha1 = (Get-FileHash $jar -Algorithm SHA1).Hash.ToLower()
    $tag = "v$version-" + $sha1.Substring(0, 7)
    $notesFile = "$out\release-notes.md"
    [IO.File]::WriteAllText($notesFile, "Лаунчер «Егерь» $version (тестовая версия)`n`nsha1: $sha1`n", (New-Object Text.UTF8Encoding $false))
    gh release create $tag "$root\release\EliumLauncher.jar" $outExe --repo $repo --title "Eger $version" --notes-file $notesFile --latest
    if ($LASTEXITCODE -ne 0) { throw 'gh release create failed' }
    Write-Host "OK: опубликован $tag в $repo"
}
