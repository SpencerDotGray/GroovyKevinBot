
from discord.ext import commands
from discord import FFmpegOpusAudio, FFmpegAudio, FFmpegPCMAudio, PCMVolumeTransformer
import discord
from datetime import datetime, time, timedelta
import asyncio
from discord.player import AudioSource
import requests
import json
import os
import pafy

client = discord.Client()
song_queue = []

try:
    with open('./auth_tokens.json', 'r') as filein:
        token = json.load(filein)['token'] 
except FileNotFoundError:
    token = os.environ.get('token')

bot = commands.Bot(command_prefix="!")
current_song = None
FFMPEG_OPTIONS = {
    'options': '-vn'
}

def get_song_info(link):
    result = pafy.new(link)
    audio = result.streams[0]
    return {
        'title': result.title,
        'source': PCMVolumeTransformer(FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)),
        'link': link
    }


@bot.command()
async def play(ctx):
    if len(bot.voice_clients) == 0:
        await ctx.send('Groovy Kevin must be in a voice channel for this command')
    else:
        if bot.voice_clients[0].is_paused():
            bot.voice_clients[0].resume()
            await ctx.send('Music resumed')
        else:
            if len(song_queue) == 0:
                await ctx.send('No music in queue.\nPlease add some')
            else:
                song = get_song_info(song_queue.pop())
                current_song = song
                voice = bot.voice_clients[0]
                            
                bot.voice_clients[0].play(song['source'])
                await ctx.send(f'Playing: {song["title"]}')

@bot.command()
async def skip(ctx):
    if len(song_queue) == 0:
        bot.voice_clients[0].stop()
        await ctx.send('No more songs in queue')
    else:
        bot.voice_clients[0].stop()
        voice = bot.voice_clients[0]
        song = get_song_info(song_queue.pop())
        current_song = song
                    
        bot.voice_clients[0].play(song['source'])
        await ctx.send(f'Playing: {song["title"]}')


@bot.command()
async def queue(ctx):

    message = ctx.message.content
    splits = message.split(' ')

    if len(splits) >= 2 and splits[1] == '-show':
        em = discord.Embed()
        for index, song in enumerate(song_queue):
            song_info = get_song_info(song)
            em.add_field(name=f'{index+1}.) {song_info["title"]}', value=f'{song_info["link"]}', inline=False)
        await ctx.send('', embed=em)
    elif len(splits) >= 2 and splits[1] == '-empty':
        song_queue.clear()
        em = discord.Embed()
        em.add_field(value='Queue emptied', inline=False)
        await ctx.send('', embed=em)
    elif len(splits) >= 2:
        song_queue.append(splits[1])
        song = get_song_info(song_queue[-1])
        em = discord.Embed()
        em.add_field(name='Song Queued', value=f'{song["title"]} - {song["link"]}', inline=False)
        await ctx.send('', embed=em)

@bot.command()
async def pause(ctx):
    if bot.voice_clients[0].is_playing():
        bot.voice_clients[0].pause()
        await ctx.send('Music paused')

@bot.command()
async def stop(ctx):
    if bot.voice_clients[0].is_playing():
        bot.voice_clients[0].stop()
        await ctx.send('Music stopped')
        current_song = None

@bot.command()
async def join(ctx):
    if len(bot.voice_clients) == 1:
        await ctx.send('I am already started and can only be in one voice channel at a time')
    else:
        voice = ctx.message.author.voice
        if not voice:
            await ctx.send('You must be connected to a voice channel for this command')
        else:
            await voice.channel.connect()


@bot.command()
async def leave(ctx):
    for x in bot.voice_clients:
        await x.disconnect()


if __name__ == "__main__":
    print(f'Online with token: {token}')
    bot.run(token)