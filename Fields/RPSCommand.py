from random import choices

async def RPSCommand(self, ctx, item):
    substring = ['rock','rocks','paper','papers','scissor','scissors','✂️','🪨','🧻']
    item = item.lower()
    if any(_ in item for _ in substring):
        whowin = choices(['I win!','You win!'], k=1, weights=[100,5])[0]
        if item == 'scissor':
            item = item + 's'
        elif item == 'rocks' or item == 'papers':
            item = item[:-1]
        if whowin == 'I win!':
            winItem = {"rock": "paper",
                        "paper": "scissors",
                        "scissors": "rock"}

            await ctx.send(f"{winItem[item]}. {whowin} You do know I'm a quantum kat, right?")
        else:
            winItem = {"paper": "rock",
                        "scissors": "paper",
                        "rock": "scissors"}
            await ctx.send(f'{winItem[item]}. {whowin}')
    else:
        await ctx.send('Rock, paper or scissors required')