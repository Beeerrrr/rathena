param(
  [string]$Format = 'yyyy-MM-dd HH:mm'
)
[Console]::Write((Get-Date).ToString($Format))

