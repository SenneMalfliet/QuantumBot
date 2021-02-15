import asyncio
import discord
from discord.ext import commands
import requests
from discord.utils import get
import json
import requests
import random
from html import unescape

client = commands.Bot(command_prefix=commands.when_mentioned_or("/"))
key = open('key.txt', 'r').read()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Streaming(name='Beter dan CoockieBot', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))


@client.event
async def on_message(ctx):
    if (ctx.author.bot): return
    if ('sigaar' in ctx.content or 'sigaren' in ctx.content):
        await ctx.channel.send(file=discord.File('sigaar.gif'))

    if (ctx.content == '/quiz'):
        await ctx.delete()
        response = requests.get('https://opentdb.com/api.php?amount=1&category=9&type=multiple')
        response = json.loads(response.content)
        question = unescape(response['results'][0]['question'])
        category = unescape(response['results'][0]['category'])

        correctAnswer = unescape(response['results'][0]['correct_answer'])
        incorrectAnswers = response['results'][0]['incorrect_answers']
        answers = [correctAnswer]
        for i in incorrectAnswers:
            answers.append(unescape(i))
        random.shuffle(answers)

        #send message and reactions
        message = await ctx.channel.send(question + "\nCategory: " + category + "\n 🇦: " + answers[0] + "\n 🇧: " + answers[1] + "\n 🇨: " + answers[2] + "\n 🇩: " + answers[3])
        await message.add_reaction("\U0001F1E6")
        await message.add_reaction("\U0001F1E7")
        await message.add_reaction("\U0001F1E8")
        await message.add_reaction("\U0001F1E9")

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check) # wachten op reactie voor 10 seconden
        except asyncio.TimeoutError:
            await message.channel.send('te laat (binnen de 10 seconden antwoorden)')

        else:
            if reaction.emoji == "🇦":
                if answers[0] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct!")
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was: " + correctAnswer)
            elif reaction.emoji == "🇧":
                if answers[1] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct!")
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was: " + correctAnswer)
            elif reaction.emoji == "🇨":
                if answers[2] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct!")
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was: " + correctAnswer)
            elif reaction.emoji == "🇩":
                if answers[3] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct!")
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was: " + correctAnswer)
client.run(key)
