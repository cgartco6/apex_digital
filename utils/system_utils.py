import os
import subprocess
import psutil
import logging
import schedule
import time

def monitor_system_resources():
    """Check system resource usage"""
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": cpu_percent,
        "memory": mem.percent,
        "disk": disk.percent,
        "status": "OK" if cpu_percent < 80 and mem.percent < 80 else "WARNING"
    }

def backup_to_cloud(source_dir, service='google_drive'):
    """Backup data to cloud storage"""
    if service == 'google_drive':
        # Requires rclone configured
        cmd = f"rclone copy {source_dir} gdrive:apex_backup -v"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return "Backup successful"
    
    return "Backup failed"

def upgrade_ai_tool(tool_name):
    """Upgrade from free to paid tools"""
    upgrade_scripts = {
        'gpt': 'upgrade_gpt.bat',
        'leonardo': 'upgrade_leonardo.bat',
        'elevenlabs': 'upgrade_elevenlabs.bat'
    }
    
    if tool_name in upgrade_scripts:
        try:
            subprocess.run([upgrade_scripts[tool_name]], check=True)
            return f"{tool_name} upgraded successfully"
        except Exception as e:
            return f"Upgrade failed: {str(e)}"
    return "Invalid tool name"

def schedule_daily_tasks():
    """Schedule recurring system tasks"""
    # Daily backup at 2AM
    schedule.every().day.at("02:00").do(
        backup_to_cloud, source_dir='./data', service='google_drive'
    )
    
    # Revenue check every 6 hours
    schedule.every(6).hours.do(
        process_owner_salary  # From payment_utils
    )
    
    # System monitoring every 30 minutes
    schedule.every(30).minutes.do(
        monitor_system_resources
    )
    
    # Run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)

def optimize_windows_performance():
    """Apply Windows performance tweaks"""
    tweaks = [
        'powercfg /setactive SCHEME_BALANCED',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 26 /f',
        'reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f'
    ]
    
    for cmd in tweaks:
        subprocess.run(cmd, shell=True, check=True)
    
    return "Windows performance optimized"
