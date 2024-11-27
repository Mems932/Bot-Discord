import discord
import os
from discord.ext import commands
import yt_dlp as youtube_dl  # Utilisation de yt-dlp pour une meilleure compatibilité
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Définir le chemin vers FFmpeg
FFMPEG_PATH = r"C:\Users\MehdiBENKHELIFA\Downloads\ffmpeg-2024-11-25-git-04ce01df0b-essentials_build\ffmpeg-2024-11-25-git-04ce01df0b-essentials_build\bin\ffmpeg.exe"

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

    # Joue la musique
    try:
        ydl_opts = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']

            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(url2, executable=FFMPEG_PATH), after=lambda e: print(f"Erreur : {e}" if e else "Lecture terminée"))
            
            await ctx.send(f"En train de jouer : **{info['title']}**")
        while voice.is_playing(): #Checks if voice is playing
            await asyncio.sleep(1) #While it's playing it sleeps for 1 second
        else:
            await asyncio.sleep(15) #If it's not playing it waits 15 seconds
        while voice.is_playing(): #and checks once again if the bot is not playing
            break #if it's playing it breaks
        else:
            await voice.disconnect() #if not it disconnects

    except youtube_dl.DownloadError as e:
        await ctx.send(f"Erreur de téléchargement : {e}")
    except discord.errors.ClientException as e:
        await ctx.send(f"Erreur Discord : {e}")
    except Exception as e:
        await ctx.send(f"Erreur : Impossible de jouer la musique. {e}")
        
  
# Commande pour arrêter la musique
@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Musique arrêtée et bot déconnecté.")
    else:
        await ctx.send("Je ne suis pas connecté à un salon vocal.")

# Lancer le bot
bot.run(os.getenv("JETON"))
