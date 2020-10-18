import os
import time
import math
import asyncio
import shutil
import glob
import subprocess
import googleapiclient
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from telethon import types
from collections import deque


from html import unescape
import requests
from googleapiclient.discovery import build
#from SaitamaRobot import YOUTUBE_API_KEY
from SaitamaRobot import LOGGER, telethn
from telethon import types, events
from telethon.tl import functions
from telethon.tl.types import DocumentAttributeAudio

# Check if user has admin rights
async def is_register_admin(chat, user, client):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (await client(functions.channels.GetParticipantRequest(chat, user))).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await client.get_peer_id(user)
        ps = (await client(functions.messages.GetFullChatRequest(chat.chat_id))) \
            .full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator)
        )
    else:
        return None

@telethn.on(events.NewMessage(pattern="^/yt(audio|video) (.*)"))
async def download_video(v_url):
    
    url = v_url.pattern_match.group(2)
    type = v_url.pattern_match.group(1).lower()
    lmao = await v_url.reply("`Preparing to download...`")
    if type == "audio":
        opts = {
            'format':
            'bestaudio',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'writethumbnail':
            True,
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'outtmpl':
            '%(id)s.mp3',
            'quiet':
            True,
            'logtostderr':
            False
        }
        video = False
        song = True
    elif type == "video":
        opts = {
            'format':
            'best',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
            '%(id)s.mp4',
            'logtostderr':
            False,
            'quiet':
            True
        }
        song = False
        video = True
    try:
        await lmao.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await lmao.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await lmao.edit("`The download content was too short.`")
        return
    except GeoRestrictedError:
        await lmao.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
        )
        return
    except MaxDownloadsReached:
        await lmao.edit("`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await lmao.edit("`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await lmao.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await lmao.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await lmao.edit("`There was an error during info extraction.`")
        return
    except Exception as e:
        await lmao.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if song:
        await lmao.edit(f"`Preparing to upload song:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{ytdl_data['id']}.mp3",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(duration=int(ytdl_data['duration']),
                                       title=str(ytdl_data['title']),
                                       performer=str(ytdl_data['uploader']))
            ])
        os.remove(f"{ytdl_data['id']}.mp3")
    elif video:
        await lmao.edit(f"`Preparing to upload video:`\
       \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{ytdl_data['id']}.mp4",
            supports_streaming=True,
            caption=ytdl_data['title'])
        os.remove(f"{ytdl_data['id']}.mp4")
                  
                  
@telethn.on(events.NewMessage(pattern="^/song (.*)"))
async def _(event):
    song = url = event.pattern_match.group(1) + " " + "song"
    if not song:
        await event.reply("`Enter song name`")
        return
    await event.edit("Processing...") 
    await event.reply("`Fetching data, please wait..`")
    os.system(f"youtube-dl -x --audio-format mp3 --add-metadata --embed-thumbnai 'ytsearch:{song}'")
    l = glob.glob("*.mp3")
    if not l:
        await event.edit("`Song not found`")
        return
    await event.client.send_file(event.chat_id, l, supports_streaming=True, reply_to=event.message)
    #await reply.delete()
    subprocess.check_output("rm -rf *.mp3",shell=True)

YOUTUBE_API_KEY = "AIzaSyABkn6rhdDXiv7MYN0kYG8sd4jJ_PJdnZA"

@telethn.on(events.NewMessage(pattern="^/yt (.*)"))
async def yts_search(video_q):
    # For .yts command, do a YouTube search from Telegram.
    if video_q.is_group:
     if not (await is_register_admin(video_q.input_chat,video_q.message.sender_id)):
       return
    query = video_q.pattern_match.group(1)
    result = ''

    if not YOUTUBE_API_KEY:
        await video_q.reply(
            "`Error: YouTube API key missing! Add it to environment vars or config.env.`"
        )
        return

   
    full_response = await youtube_search(query)
    videos_json = full_response[1]

    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        result += f"{title}\n{link}\n\n"

    reply_text = f"**Search Query:**\n`{query}`\n\n**Results:**\n\n{result}"

    await video_q.reply(reply_text, link_preview=False)


async def youtube_search(query,
                         order="relevance",
                         token=None,
                         location=None,
                         location_radius=None):
    """ Do a YouTube search. """
    youtube = build('youtube',
                    'v3',
                    developerKey=YOUTUBE_API_KEY,
                    cache_discovery=False)
    search_response = youtube.search().list(
        q=query,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",
        maxResults=10,
        location=location,
        locationRadius=location_radius).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return (nexttok, videos)               
  
__help__ = """
*Song Download*
 x /song <text>: Downloads and Uploads The song!
*Youtube Search*
 x /yt <text>: perform a youtube search
 
 *Youtube Downloader*
 x /ytaudio <link> : Gives you direct mp3 audio 
 x /ytvideo <link>: Gives you direct mp4 video 
*NOTE*
Bot Downloads to server then uploads to the telegram . so have patience !
Only group admins will able to use this command , others simply can use in bot's pm[!](https://telegra.ph/file/74b9a1bf04e93fc774d7b.png)
"""
__mod_name__ = "Youtube"
