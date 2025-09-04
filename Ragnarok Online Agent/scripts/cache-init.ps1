param([switch]$Force,[string]$Root)
$toolRoot = if ($PSBoundParameters.ContainsKey('Root') -and $Root) {(Resolve-Path -LiteralPath $Root).Path} else {Split-Path $PSScriptRoot -Parent}
Write-Output ("Cache init at: {0}" -f $toolRoot)
$templates = Get-ChildItem -Path $toolRoot -Recurse -File -Filter '*_template.*' -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -match 'ANALYSIS_CACHE|CACHE' }
$copied=0; foreach($tpl in $templates){$dest=Join-Path $tpl.DirectoryName ($tpl.Name -replace '_template',''); if((Test-Path -LiteralPath $dest)-and -not $Force){continue}; Copy-Item -LiteralPath $tpl.FullName -Destination $dest -Force; $copied++; Write-Output ("Copied: {0} -> {1}" -f $tpl.FullName,$dest)}
Write-Output ("Cache init complete. Files created/updated: {0}" -f $copied)

