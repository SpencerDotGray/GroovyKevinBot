
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
channel_id = 901364781808746526 # Put your channel id here
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
                    
        bot.voice_clients[0].play(song['source'])
        await ctx.send(f'Playing: {song["title"]}')

@bot.command()
async def showqueue(ctx):
    output = 'Queue:'
    for index, song in enumerate(song_queue):
        song_info = get_song_info(song)
        output += f'{index}.) {song_info["title"]} - {song_info["link"]}'
    await ctx.send(output)

@bot.command()
async def queue(ctx):
    url = ctx.message.content
    url = url.replace('!queue ', '')
    song_queue.append(url)
    await ctx.send('Song queued')

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