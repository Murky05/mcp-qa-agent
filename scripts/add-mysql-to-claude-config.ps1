# Adds (or updates) the "mysql" MCP server in Claude Desktop's config.
# Asks for the MySQL password at runtime and backs up the config first.
# Usage: run in PowerShell:  .\add-mysql-to-claude-config.ps1

$pw = Read-Host "MySQL root password"
$db = Read-Host "Database name (default: vikhyatacademy)"
if (-not $db) { $db = "vikhyatacademy" }

$py = "$env:LOCALAPPDATA\Programs\Python\Python313"
$srv = [pscustomobject]@{
  command = "$py\Scripts\uv.exe"
  args    = @("--directory", "$py\Lib\site-packages", "run", "mysql_mcp_server")
  env     = [pscustomobject]@{
    MYSQL_HOST = "127.0.0.1"; MYSQL_PORT = "3306"; MYSQL_USER = "root"
    MYSQL_PASSWORD = $pw; MYSQL_DATABASE = $db
  }
}

# Claude's config can live in either place depending on the install
$files = Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\claude_desktop_config.json",
                       "$env:APPDATA\Claude\claude_desktop_config.json" -ErrorAction SilentlyContinue |
         ForEach-Object FullName
if (-not $files) { Write-Host "Config not found. Open Claude > Settings > Developer > Edit Config once first." -ForegroundColor Red; return }

foreach ($cfg in $files) {
  Copy-Item $cfg "$cfg.bak" -Force
  $j = Get-Content $cfg -Raw | ConvertFrom-Json
  if (-not $j.mcpServers) { $j | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) }
  $j.mcpServers | Add-Member -NotePropertyName mysql -NotePropertyValue $srv -Force
  # UTF-8 without BOM so Claude can parse it
  [IO.File]::WriteAllText($cfg, ($j | ConvertTo-Json -Depth 20))
  Write-Host "Updated $cfg (backup: $cfg.bak)" -ForegroundColor Green
}
Write-Host "Now quit Claude from the system tray and reopen it."
