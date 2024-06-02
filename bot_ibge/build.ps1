$exclude = @("venv", "bot_ibge.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot_ibge.zip" -Force