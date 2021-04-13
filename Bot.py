import asyncio
import discord
from discord.ext import commands
from discord.utils import get
import json
import requests
import random
from html import unescape
from akinator.async_aki import Akinator
import akinator
import youtube_dl
import wikipedia
import re
from wikipedia import DisambiguationError, PageError

client = commands.Bot(command_prefix=commands.when_mentioned_or("/"))
key = open('key.txt', 'r').read()
aki = Akinator()
wikipedia.set_lang('nl')
emoji_alphabet = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


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

    if ctx.content == '/role':
        roles = ctx.guild.roles
        print(roles)

    if ctx.content == '/lofi':
        channel = ctx.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()
            print(f"The bot has connected to {channel}\n")

            player = await YTDLSource.from_url('https://www.youtube.com/watch?v=5qap5aO4i9A', loop=client.loop, stream=True)
            ctx.guild.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    if ctx.content == '/leave':
        channel = ctx.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"The bot has left {channel}")
        else:
            print("Bot was told to leave voice channel, but was not in one")

    if ctx.content.startswith('/wiki '):
        query = re.sub("/wiki ", "", ctx.content)
        try:
            page = wikipedia.page(query, auto_suggest=True, redirect=True)
            await ctx.channel.send(page.summary[:1900] + "... \nMeer lezen: <" + page.url + ">")
        except DisambiguationError as disambiguation:
            disambiguation_response = "bedoelde je: \n"
            for i in range(len(disambiguation.options)):
                disambiguation_response += emoji_alphabet[i] + disambiguation.options[i] + "\n"
            response = await ctx.channel.send(disambiguation_response)
            for i in range(len(disambiguation.options)):
                await response.add_reaction(emoji_alphabet[i])

            def check(reaction, user):
                return user == ctx.author

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)  # wachten op reactie voor 20 seconden
            except asyncio.TimeoutError:
                await response.delete()
            else:
                if reaction.emoji in emoji_alphabet:
                    await response.delete()
                    query = disambiguation.options[emoji_alphabet.index(reaction.emoji)]
                    try:
                        page = wikipedia.page(query, auto_suggest=True, redirect=True)
                        await ctx.channel.send(page.summary[:1900] + "... \nMeer lezen: <" + page.url + ">")
                    except DisambiguationError or PageError:
                        await ctx.channel.send("Er is iets fout gegaan maar het is niet Senne zijn fout, waarschijnlijk is de API van wikipedia weer brak of heeft Ruben weer iets kapot gemaakt.")
        except PageError:
            await ctx.channel.send("Geen pagina gevonden met de Titel: " + query)

    if ctx.content == '/quiz':
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
        message = await ctx.channel.send(question + "\n 🇦: " + answers[0] + "\n 🇧: " + answers[1] + "\n 🇨: " + answers[2] + "\n 🇩: " + answers[3])
        for i in range(4):
            await message.add_reaction(emoji_alphabet[i])

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check) # wachten op reactie voor 15 seconden
        except asyncio.TimeoutError:
            await message.channel.send('te laat (binnen de 15 seconden antwoorden)')

        else:
            if reaction.emoji in emoji_alphabet:
                index = emoji_alphabet.index(reaction.emoji)
                if answers[index] == correctAnswer:
                    await message.edit(content=message.content + "\n Correct! Het antwoord was inderdaad " + correctAnswer)
                else:
                    await message.edit(content=message.content + "\n Fout! Het juiste antwoord was " + correctAnswer)
                await message.clear_reactions()

async def akinatorGame(ctx):
    q = await aki.start_game('nl', True)
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
            await message.delete()

        else:

            if reaction.emoji == "🟩": #groen
                a = "y"
            elif reaction.emoji == "🟧": #oranje
                a = "i"
            elif reaction.emoji == "🟥": #rood
                a = "n"
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
        elif reaction.emoji == "🟥":  # rood
            await message.edit(content=message.content + "\nJammer... Ik zal volgende keer beter mijn best doen.")
        await message.clear_reactions()


client.run(key)
