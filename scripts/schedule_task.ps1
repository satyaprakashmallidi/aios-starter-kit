$action = New-ScheduledTaskAction -Execute 'E:\Github Projects\AIOS\aios-starter-kit\aios-starter-kit\.venv\Scripts\python.exe' -Argument 'scripts\collect.py' -WorkingDirectory 'E:\Github Projects\AIOS\aios-starter-kit\aios-starter-kit'
$trigger = New-ScheduledTaskTrigger -Daily -At '6am'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'AIOS-DataCollect' -Trigger $trigger -Action $action -Settings $settings -Force
Write-Host 'AIOS daily collection scheduled for 6:00 AM'
