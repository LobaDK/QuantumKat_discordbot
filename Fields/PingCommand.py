from time import time
from ntplib import NTPClient
from random import choice

async def PingCommand(self, ctx, ping_mode):
    LatencyResponses = ['Fiber is fast and all but they really should consider swapping to QuantumCables:tm:.',"You know, I could've quantised *at least* 100x the amount of data in that time.", 'That was a nice nap.', "Do you realize how many times I could've been pet in that amount of time!", 'And so close to beating your alternate-self from another dimension too!', "Let's just not tell your alternate-self from another dimension..."]

    if ctx.message.content.startswith('?ping'):
        pingresponse = 'pong'
    
    elif ctx.message.content.startswith('?pong'):
        pingresponse = 'ping'
    
    if ping_mode:
        if ping_mode.lower() == 'latency':
            
            #Get current local time on the machine clock and multiply by 1000 to get milliseconds
            local_time_in_ms = (round(time() * 1000))

            #Get the time the message was sent in milliseconds by multiplying by 1000
            message_timestamp = (round(ctx.message.created_at.timestamp() * 1000))

            #Get latency in milliseconds by subtracting the current time, with the time the message was sent
            latency = local_time_in_ms - message_timestamp

            #If the latency is negative i.e. system clock is behind the real world by more than the latency
            #Get a rough estimate of the latency instead, by taking the offset, turning it into milliseconds, and adding it to the latency
            if latency < 0:
                c = NTPClient()
                response = c.request('pool.ntp.org', version=3)
                offset = round(response.offset * 1000)
                latency += offset
                await ctx.send(f'A negative latency value was detected. Used pool.ntp.org to attempt to correct, with a {round(offset)}ms offset.')


            await ctx.send(f'{pingresponse}! Took {latency * 2}ms. {choice(LatencyResponses)}\nConnection to discord: {round(self.bot.latency * 1000)}ms')
        else:
            await ctx.send("Only 'latency' parameter allowed")
    else:
        await ctx.send(pingresponse)