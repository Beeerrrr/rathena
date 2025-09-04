param([string]$Root)
$toolRoot = if ($PSBoundParameters.ContainsKey('Root') -and $Root) {(Resolve-Path -LiteralPath $Root).Path} else {Split-Path $PSScriptRoot -Parent}
$files = Get-ChildItem -Path $toolRoot -Recurse -File -Filter '*.json' -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -match 'ANALYSIS_CACHE|CACHE' }
if (-not $files) { Write-Output 'No JSON files found under cache directories.'; exit 0 }
$failed = $false; foreach ($f in $files) { try { $null = Get-Content -Raw -LiteralPath $f.FullName | ConvertFrom-Json -ErrorAction Stop; Write-Output ("OK   {0}" -f $f.FullName) } catch { Write-Output ("FAIL {0}: {1}" -f $f.FullName, $_.Exception.Message); $failed = $true } }
if ($failed) { exit 1 } else { exit 0 }

