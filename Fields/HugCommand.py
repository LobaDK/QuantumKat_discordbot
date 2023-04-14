from random import randint, choice
from num2words import num2words
async def HugCommand(self, ctx, optional_user_or_object):
    quantum_amount = randint(1,20)
    if quantum_amount == 1:
        verb = 'time'
    else:
        verb = 'times'
    quantumspan = randint(0,100)

    hugs = 'hu' + 'g' * quantum_amount + 's'

    if not optional_user_or_object:
        await ctx.send(f'Superpositions {quantum_amount} {verb} around {ctx.author.mention} and {hugs}')
        return

    mention = f'<@{self.bot.user.id}>'
    if mention in optional_user_or_object:
        quantummode = choice(['purr','frequency'])
        if quantummode == 'purr':
            await ctx.send(f'Quantum purrs and entangles {ctx.author.mention} to the {num2words(quantumspan, to="ordinal_num")} {choice(["dimension","universe","reality","timeline"])}')
        elif quantummode == 'frequency':
            await ctx.send(f'Quantum vibrates at {randint(1,100_000)}hz, teleporting {choice(["a chair","a table","a vase","a long-lost creditcard","some strangers phone","a stranger","an error","a bucket","a bucket of milk","||redacted||","a cat","a quantum cat","an alien from the 7th dimension","a blackhole","a random star","a random planet"])} from the {num2words(quantumspan, to="ordinal_num")} {choice(["dimension","universe","reality","timeline"])}')
    else:
        await ctx.send(f'Superpositions {quantum_amount} {verb} around {optional_user_or_object} and {hugs}')