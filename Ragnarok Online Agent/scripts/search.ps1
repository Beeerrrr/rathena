param(
  [Parameter(Mandatory=$true)][string]$Pattern,
  [string]$Path = '.',
  [switch]$Regex
)

function Has-Command($name) {
  $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

if (Has-Command 'rg') {
  $args = @('-n','--hidden','--no-heading',$Pattern,$Path)
  if (-not $Regex) { $args = @('--fixed-strings') + $args }
  & rg @args
  exit $LASTEXITCODE
}

$files = Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue
$selectArgs = @{ Pattern = $Pattern; CaseSensitive = $false }
if (-not $Regex) { $selectArgs.SimpleMatch = $true }
$matches = $files | Select-String @selectArgs

foreach ($m in $matches) {
  $col = if ($m.Matches.Count -gt 0) { $m.Matches[0].Index + 1 } else { 1 }
  Write-Output ("{0}:{1}:{2}:{3}" -f $m.Path,$m.LineNumber,$col,$m.Line)
}

