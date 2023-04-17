from random import randint, choice

async def QuantumHugCommand(self, ctx, optional_user_or_object):
    mention = f'<@{self.bot.user.id}>'
    quantum_amount = randint(100,1000)
    qhugs = 'hu' + 'g' * int(str(quantum_amount)[:2]) + 's'
    if not optional_user_or_object:
        await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {ctx.author.mention}')
    elif mention in optional_user_or_object:
        quantumhugloop = ""
        for _ in range(0,randint(8,40)):
            quantumhugloop = quantumhugloop + choice(['Quantum hugging the','QuantumKat','QuantumKatting the','Quantum hug'])
        await ctx.send(f'{quantumhugloop}... Instability detected, sucessfully terminated the {choice(["dimension","universe","reality","timeline","chair","table","error","object","||redacted||","corruptcorruptcorruptcorrupt","corrupt","future","past","presence","instability","stability","..."])}!')
    else:
        await ctx.send(f'Superpositions {quantum_amount} times across all timelines, dimensions, universes and realities, and {qhugs} {optional_user_or_object}')