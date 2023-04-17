from glob import glob

async def aaaaCountCommand(self, ctx):
    extensions = ['*.gif', '*.jpeg', '*.jpg', '*.mov', '*.mp3', '*.mp4', '*.png', '*.webm', '*.webp']
    all_files = []
    for extension in extensions:
        current_extension = glob.glob(f'/var/www/aaaa/{extension}')
        all_files += current_extension
    await ctx.send(f'There are currently {len(all_files)} quantised datasets.')