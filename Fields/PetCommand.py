import random

async def PetCommand(self, ctx, optional_user_or_object):
    quantum_amount = random.randint(1,20)
    if quantum_amount == 1:
        verb = 'time'
    else:
        verb = 'times'

    pets = 'pe' + 't' * quantum_amount + 's'

    if not optional_user_or_object:
        await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {pets}')
        return

    mention = f'<@{self.bot.user.id}>'
    if mention in optional_user_or_object:
        quantumspan = random.randint(0,100)
        quantummode = random.choices(['purr','frequency','quantumloop'], k=1, weights=[10,10,2])[0]
        if quantummode == 'purr':
            await ctx.send(f'Quantum purrs across {quantumspan} {random.choices(["dimension","universe","reality","timeline","dimension, universe, realitie and timeline"], weights=[100,100,100,100,1], k=1)[0] if quantumspan == 1 else random.choices(["dimensions","universes","realities","timelines","dimensions, universes, realities and timelines"], weights=[100,100,100,100,1], k=1)[0]}')
        elif quantummode == 'frequency':
            await ctx.send(f'Quantum vibrates at {random.randint(1,100_000)}hz')
        elif quantummode == 'quantumloop':
            petloop = ""
            for _ in range(0,random.randint(8,40)):
                petloop = petloop + random.choice(['pet','pat','petting', 'patting'])
            await ctx.send(f'Quantum Loop pet initiated trying to pet self! {petloop}')
    else:
        await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {pets}')