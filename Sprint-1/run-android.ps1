# Run from this project folder after Flutter and Firebase setup.
$ErrorActionPreference = 'Stop'
if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    throw 'Flutter SDK-г PATH-д нэмнэ үү.'
}
Push-Location $PSScriptRoot
try {
    flutter pub get
    if ($LASTEXITCODE -ne 0) { throw 'flutter pub get амжилтгүй.' }
    $runArgs = @('run')
    if ($env:USE_FIREBASE_EMULATOR -eq 'true') {
        $runArgs += '--dart-define=USE_FIREBASE_EMULATOR=true'
    }
    if ($env:STRIPE_PUBLISHABLE_KEY) {
        $runArgs += "--dart-define=STRIPE_PUBLISHABLE_KEY=$env:STRIPE_PUBLISHABLE_KEY"
    }
    flutter @runArgs
    if ($LASTEXITCODE -ne 0) { throw 'flutter run амжилтгүй.' }
} finally {
    Pop-Location
}
