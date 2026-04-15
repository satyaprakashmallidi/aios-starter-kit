$conn = Get-NetTCPConnection -LocalPort 3210 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
    $procId = $conn.OwningProcess
    Write-Host "Found process $procId on port 3210"
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Process stopped"
} else {
    Write-Host "No process on port 3210"
}
