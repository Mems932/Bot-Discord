import discord
import os
from discord.ext import commands
import yt_dlp as youtube_dl  # Utilisation de yt-dlp pour une meilleure compatibilité
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Définir le chemin vers FFmpeg
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-2024-11-25-git-04ce01df0b-essentials_build\bin\ffmpeg.exe"

# Vérification manuelle de FFmpeg
if not os.path.exists(FFMPEG_PATH):
    print("Le chemin FFmpeg spécifié n'est pas valide. Vérifiez le chemin.")
    exit()  # Arrête le programme si le chemin FFmpeg n'est pas valide

print(f"FFmpeg est trouvé à : {FFMPEG_PATH}")

# Configurer les intents nécessaires
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Configurer le bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Queue de musique
music_queue = []

# Fonction pour jouer de la musique
async def play_music(ctx):
    if not music_queue:
        return

    song = music_queue[0]  # Prendre la première chanson dans la queue
    music_queue.pop(0)  # Retirer la chanson de la queue

    # Joue la musique
    try:
        ydl_opts = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song['url'], download=False)
            url2 = info['url']

            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(url2, executable=FFMPEG_PATH), after=lambda e: print(f"Erreur : {e}" if e else "Lecture terminée"))

            await ctx.send(f"En train de jouer : **{info['title']}**")
        
        while voice.is_playing():  # Vérifie si le bot joue
            await asyncio.sleep(1)  # Attends pendant que la musique joue

        await play_music(ctx)  # Re-joue la musique suivante dans la queue

    except Exception as e:
        await ctx.send(f"Erreur : Impossible de jouer la musique. {e}")

# Commande pour jouer de la musique
@bot.command(name='play')
async def play(ctx, url: str):
    # Vérifie si l'utilisateur est dans un salon vocal
    if not ctx.author.voice:
        await ctx.send("Vous devez être dans un salon vocal pour jouer de la musique.")
        return

    # Rejoint le salon vocal si le bot n'est pas déjà connecté
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        try:
            await voice_channel.connect()
        except Exception as e:
            await ctx.send(f"Erreur : Impossible de rejoindre le salon vocal. {e}")
            return

    # Ajouter la chanson à la queue
    music_queue.append({'url': url})
    await ctx.send(f"Chanson ajoutée à la queue : {url}")

    # Si le bot n'est pas en train de jouer de la musique, commence à jouer
    if not ctx.voice_client.is_playing():
        await play_music(ctx)

# Commande pour arrêter la musique
@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Musique arrêtée et bot déconnecté.")
    else:
        await ctx.send("Je ne suis pas connecté à un salon vocal.")

# Commande pour skip la musique
@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Musique skipée.")
    else:
        await ctx.send("Je ne suis pas connecté à un salon vocal.")

@bot.command(name='search')
async def search(ctx, *, query: str):
    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url2 = info['entries'][0]['url']  # Prendre la première vidéo trouvée
        music_queue.append({'url': url2})
        await ctx.send(f"Chanson ajoutée à la queue : {info['entries'][0]['title']}")
        
    # Rejoint le salon vocal si le bot n'est pas déjà connecté
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        try:
            await voice_channel.connect()
        except Exception as e:
            await ctx.send(f"Erreur : Impossible de rejoindre le salon vocal. {e}")
            return

    # Si le bot n'est pas en train de jouer, commence à jouer la musique
    if not ctx.voice_client.is_playing():
        await play_music(ctx)

# Lancer le bot
bot.run(os.getenv("JETON"))
