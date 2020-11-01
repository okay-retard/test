import os
from tswift import Song
import lyricsgenius 
#from SaitamaRobot import Bot,Update,Message,Chat
#from telegram.ext import run_async, CommandHandler, CallbackContext
from telethon import types, events
from SaitamaRobot import telethn

#from SaitamaRobot import dispatcher

GENIUS = os.environ.get("GENIUS_API_TOKEN", None)



@telethn.on(events.NewMessage(pattern="^/glyrics (.*)"))
async def lyrics(lyric):
    if lyric.pattern_match.group(1):
        query = lyric.pattern_match.group(1)
    else:
        await lyric.edit(
            "Error: please use '-' as divider for <artist> and <song> \neg: `.glyrics Nicki Minaj - Super Bass`"
        )
        return
    if r"-" in query:
        pass
    else:
        await lyric.edit(
            "Error: please use '-' as divider for <artist> and <song> \neg: `.glyrics Nicki Minaj - Super Bass`"
        )
        return
    if GENIUS is None:
        await lyric.edit(
            "`Provide genius access token to config.py or Heroku Var first kthxbye!`"
        )
    else:
        genius = lyricsgenius.Genius(GENIUS)
        try:
            args = query.split("-", 1)
            artist = args[0].strip(" ")
            song = args[1].strip(" ")
        except Exception as e:
            await lyric.edit(f"Error:\n`{e}`")
            return
    if len(args) < 1:
        await lyric.edit("`Please provide artist and song names`")
        return
    await lyric.edit(f"`Searching lyrics for {artist} - {song}...`")
    try:
        songs = genius.search_song(song, artist)
    except TypeError:
        songs = None
    if songs is None:
        await lyric.edit(f"Song **{artist} - {song}** not found!")
        return
    if len(songs.lyrics) > 4096:
        await lyric.edit("`Lyrics is too big, view the file to see it.`")
        with open("lyrics.txt", "w+") as f:
            f.write(f"Search query: \n{artist} - {song}\n\n{songs.lyrics}")
        await lyric.client.send_file(
            lyric.chat_id,
            "lyrics.txt",
            reply_to=lyric.id,
        )
        os.remove("lyrics.txt")
    else:
        await lyric.edit(
            f"**Search query**: \n`{artist} - {song}`\n\n```{songs.lyrics}```"
        )
        
        
__help__ = """
*lund hai bc*
 x /glyrics <text>: perform a youtube search
 
 
"""
__mod_name__ = "lyric"
