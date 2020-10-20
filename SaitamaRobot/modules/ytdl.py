# Thanks to @AvinashReddy3108 for this plugin
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
    sed = v_url = await edit_or_reply(v_url, "`Preparing to download...`")
    if type == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        video = False
        song = True
    elif type == "v":
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        song = False
        video = True
    try:
        await sed.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await sed.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await sed.edit("`The download content was too short.`")
        return
    except GeoRestrictedError:
        await sed.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
        )
        return
    except MaxDownloadsReached:
        await sed.edit("`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await sed.edit("`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await sed.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await sed.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await sed.edit("`There was an error during info extraction.`")
        return
    except Exception as e:
        await sed.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    catthumb = Path(f"{ytdl_data['id']}.jpg")
    if not os.path.exists(catthumb):
        catthumb = Path(f"{ytdl_data['id']}.webp")
    elif not os.path.exists(catthumb):
        catthumb = None
    if song:
        await sed.edit(
            f"`Preparing to upload song:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*"
        )
        await borg.send_file(
            sed.chat_id,
            f"{ytdl_data['id']}.mp3",
            supports_streaming=True,
            thumb=catthumb,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(ytdl_data["duration"]),
                    title=str(ytdl_data["title"]),
                    performer=str(ytdl_data["uploader"]),
                )
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d, t, v_url, c_time, "Uploading..", f"{ytdl_data['title']}.mp3"
                )
            ),
        )
        os.remove(f"{ytdl_data['id']}.mp3")
        if catthumb:
            os.remove(catthumb)
        await sed.delete()
    elif video:
        await sed.edit(
            f"`Preparing to upload video:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*"
        )
        await telethn.send_file(
            sed.chat_id,
            f"{ytdl_data['id']}.mp4",
            supports_streaming=True,
            caption=ytdl_data["title"],
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d, t, v_url, c_time, "Uploading..", f"{ytdl_data['title']}.mp4"
                )
            ),
        )
        os.remove(f"{ytdl_data['id']}.mp4")
        if catthumb:
            os.remove(catthumb)
        await sed.delete()


@telethn.on(events.NewMessage(pattern="^/yts (.*)"))
#@bot.on(sudo_cmd(pattern="yts (.*)", allow_sudo=True))
async def yt_search(video_q):
    """ For .yts command, do a YouTube search from Telegram. """
    query = video_q.pattern_match.group(1)
    result = ""
    if not Config.YOUTUBE_API_KEY:
        await edit_or_reply(
            video_q,
            "`Error: YouTube API key missing! Add it to reveal config vars in heroku or userbot/uniborgConfig.py in github fork.`",
        )
        return
    video_q = await edit_or_reply(video_q, "```Processing...```")
    full_response = await youtube_search(query)
    videos_json = full_response[1]
    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        result += f"{title}\n{link}\n\n"
    reply_text = f"**Search Query:**\n`{query}`\n\n**Results:**\n\n{result}"
    await video_q.edit(reply_text)


async def youtube_search(
    query, order="relevance", token=None, location=None, location_radius=None
):
    """ Do a YouTube search. """
    youtube = build(
        "youtube", "v3", developerKey=Config.YOUTUBE_API_KEY, cache_discovery=False
    )
    search_response = (
        youtube.search()
        .list(
            q=query,
            type="video",
            pageToken=token,
            order=order,
            part="id,snippet",
            maxResults=10,
            location=location,
            locationRadius=location_radius,
        )
        .execute()
    )
    videos = [
        search_result
        for search_result in search_response.get("items", [])
        if search_result["id"]["kind"] == "youtube#video"
    ]

    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return (nexttok, videos)
