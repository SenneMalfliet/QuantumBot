import asyncio
import discord
from discord.ext import commands
#import requests
#from discord.utils import get
import json
import requests
import random
from html import unescape
from akinator.async_aki import Akinator
import akinator

client = commands.Bot(command_prefix=commands.when_mentioned_or("/"))
key = open('key.txt', 'r').read()
aki = Akinator()


@client.event
async def on_ready():
    print('Ingelogd als {0.user}'.format(client))
    await client.change_presence(activity=discord.Streaming(name='Beter dan CoockieBot', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))


@client.event
async def on_message(ctx):
    if ctx.author.bot: return
    if 'sigaar' in ctx.content or 'sigaren' in ctx.content:
        await ctx.channel.send(file=discord.File('sigaar.gif'))

    if ' boos ' in ctx.content or ctx.content == 'boos' or ctx.content.startswith('boos ') or ctx.content.endswith(' boos') or ctx.content.endswith('boos!') or ctx.content.endswith('boos.'):
        await ctx.channel.send(file=discord.File('boos.gif'))

    if ctx.content == '/akinator':
        await akinatorGame(ctx)

    if ctx.content == '/quiz':
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
                    await message.edit(content=message.content + "\n Correct! Het antwoord was inderdaad " + correctAnswer)
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was " + correctAnswer)
                await message.clear_reactions()
            elif reaction.emoji == "🇧":
                if answers[1] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct! Het antwoord was inderdaad " + correctAnswer)
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was " + correctAnswer)
                await message.clear_reactions()
            elif reaction.emoji == "🇨":
                if answers[2] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct! Het antwoord was inderdaad " + correctAnswer)
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was " + correctAnswer)
                await message.clear_reactions()
            elif reaction.emoji == "🇩":
                if answers[3] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct! Het antwoord was inderdaad " + correctAnswer)
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was " + correctAnswer)
                await message.clear_reactions()


async def akinatorGame(ctx):
    q = await aki.start_game('nl')
    message = await ctx.channel.send(q)
    await message.add_reaction("\U0001F7E9")
    await message.add_reaction("\U0001F7E7")
    await message.add_reaction("\U0001F7E5")
    await message.add_reaction("\U0001F448")

    def check(reaction, user):
        return user == ctx.author

    while aki.progression <= 80:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.edit(content='niet geantwoord binnen de minuut.')

        else:

            if reaction.emoji == "🟩": #groen
                a = "y"
                await message.remove_reaction(reaction.emoji, user)
            elif reaction.emoji == "🟧": #oranje
                a = "i"
                await message.remove_reaction(reaction.emoji, user)
            elif reaction.emoji == "🟥": #rood
                a = "n"
                await message.remove_reaction(reaction.emoji, user)
            elif reaction.emoji == "👈": #terug
                a = "b"
                await message.remove_reaction(reaction.emoji, user)

            if a == "b":
                try:
                    q = await aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            else:
                q = await aki.answer(a)
            await message.edit(content=q)

    await aki.win()
    await message.edit(content=f"Het is {aki.first_guess['name']} ({aki.first_guess['description']})! Was ik juist?\n{aki.first_guess['absolute_picture_path']}\n\t")
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await message.clear_reactions()
    else:
        if reaction.emoji == "🟩":  # groen
            await message.edit(content=message.content + "\nJoepie!")
            await message.remove_reaction(reaction.emoji, user)
        elif reaction.emoji == "🟥":  # rood
            await message.edit(content=message.content + "\nJammer... Ik zal volgende keer beter mijn best doen.")
            await message.remove_reaction(reaction.emoji, user)
        await message.clear_reactions()


client.run(key)
