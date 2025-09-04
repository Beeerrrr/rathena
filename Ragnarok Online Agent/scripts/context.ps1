Param(
  [Parameter(Mandatory = $true)][ValidateSet('get','set','append','log','dump')][string]$Command,
  [string]$Key,
  [string]$Value,
  [string]$Component,
  [string]$Event,
  [string[]]$Data
)

$cli = Join-Path -Path (Get-Location) -ChildPath "scripts/context-cli.py"
if (-Not (Test-Path $cli)) { throw "context-cli.py not found: $cli" }

switch ($Command) {
  'get' { python $cli get $Key }
  'set' { python $cli set $Key $Value }
  'append' { python $cli append $Key $Value }
  'log' { python $cli log $Component $Event @Data }
  'dump' { python $cli dump }
}

