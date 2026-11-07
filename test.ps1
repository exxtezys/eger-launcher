# Компилирует лаунчер вместе с tests\*.java и запускает каждый тест (класс test.<Имя>).
# Тесты не попадают в EliumLauncher.jar: build.ps1 собирает только src\.
param([string[]]$Only)
$ErrorActionPreference = 'Stop'
$jdk = 'C:\Program Files\Java\jdk-21\bin'
$root = $PSScriptRoot
$out = Join-Path $env:TEMP 'eger-tests'
Remove-Item -Recurse -Force $out -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$out\classes" | Out-Null
$src = @(Get-ChildItem -Recurse "$root\src" -Filter *.java | ForEach-Object FullName)
$tests = @(Get-ChildItem "$root\tests" -Filter *Test.java | ForEach-Object FullName)
& "$jdk\javac.exe" --release 21 -encoding UTF-8 -d "$out\classes" ($src + $tests)
if ($LASTEXITCODE -ne 0) { throw 'javac failed' }
Copy-Item "$root\src\launcher.properties" "$out\classes\"
$names = $tests | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_) }
if ($Only) { $names = $names | Where-Object { $Only -contains $_ } }
$failed = @()
foreach ($n in $names) {
    $ErrorActionPreference = 'Continue'
    $res = & "$jdk\java.exe" -cp "$out\classes" "test.$n" 2>$null
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    $last = ($res | Select-Object -Last 1)
    if ($code -eq 0) { Write-Host "PASS $n" } else { Write-Host "FAIL $n"; $res | ForEach-Object { Write-Host "  $_" }; $failed += $n }
}
Write-Host ("{0}/{1} passed" -f ($names.Count - $failed.Count), $names.Count)
if ($failed.Count -gt 0) { exit 1 }
