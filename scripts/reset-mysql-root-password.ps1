# Resets the MySQL 8.0 root password on Windows.
# MUST be run in PowerShell opened with "Run as administrator".
# Assumes the default service name (MySQL80) and install paths.

$bin = "C:\Program Files\MySQL\MySQL Server 8.0\bin"
$ini = "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"
$new = Read-Host "Choose a NEW MySQL root password"

Stop-Service MySQL80
Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force

Set-Content C:\mysql-init.txt "ALTER USER 'root'@'localhost' IDENTIFIED BY '$new';" -Encoding ASCII
$p = Start-Process "$bin\mysqld.exe" -ArgumentList "--defaults-file=`"$ini`"", '--init-file=C:\\mysql-init.txt' -PassThru -WindowStyle Hidden
Start-Sleep 20

& "$bin\mysqladmin.exe" -u root "-p$new" shutdown
Start-Sleep 5; if (!$p.HasExited) { Stop-Process $p -Force }
Remove-Item C:\mysql-init.txt   # don't leave the password on disk

Start-Service MySQL80
& "$bin\mysql.exe" -u root "-p$new" -e "SELECT 'Password reset worked' AS result;"
