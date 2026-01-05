# Setup project directory structure

$directories = @(
    "src\agents",
    "src\chains",
    "src\tools",
    "src\loaders",
    "src\prompts",
    "src\memory",
    "src\callbacks",
    "src\api\routes",
    "src\api\models",
    "tests\unit",
    "tests\integration",
    "tests\e2e",
    "docs",
    "scripts",
    "data\chroma",
    "logs"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir"
    }
}

Write-Host "`nDirectory structure created successfully!"

