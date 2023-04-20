from psutil import cpu_percent, virtual_memory, disk_usage

async def StatusCommand(self, ctx):
    await ctx.send(f'''
Current CPU Usage: {cpu_percent(1)}%
RAM: {int(virtual_memory().used / 1024 / 1024)}MB / {int(virtual_memory().total / 1024 / 1024)}MB | {virtual_memory().percent}%
Primary disk: {int(disk_usage('/').used / 1024 / 1024 / 1000)}GB / {int(disk_usage('/').total / 1024 / 1024 / 1000)}GB | {disk_usage('/').percent}%
''')