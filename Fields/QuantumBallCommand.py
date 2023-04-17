from random import randint, choice, choices

async def QuantumBallCommand(self, ctx):
    affirmative_answers_list = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes definitely.', 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.']
    non_committal_answers_list = ['Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.']
    negative_answers_list = ["Don't count on it.", 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
    reason_list = ['Quantum tunnel unexpectedly collapsed!', 'Entanglement lost!', 'Was that vase always broken?', 'Error', '||redacted||', 'Universal instability detected!']
    quantumball_messages_list = ['{amount} {location} agrees or already happened in. {affirmative_answer}', '{reason}. {non_committal_answer}', 'No related parallel universe, dimension, timeline or reality detected! {negative_answer}']

    amount = randint(100, 100_000)

    await ctx.send(choices(quantumball_messages_list, k=1, weights=[10, 5, 5])[0].format(amount=amount, location=choice(['realities','universes','dimensions','timelines']), affirmative_answer=choice(affirmative_answers_list), reason=choice(reason_list), non_committal_answer=choice(non_committal_answers_list), negative_answer=choice(negative_answers_list)))