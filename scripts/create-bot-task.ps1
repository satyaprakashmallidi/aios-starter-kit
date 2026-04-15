$action = New-ScheduledTaskAction -Execute "E:\Github Projects\AIOS\aios-starter-kit\aios-starter-kit\run-telegram-bot.bat"
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "AIOS-TelegramBot" -Action $action -Trigger $trigger -Settings $settings -Force