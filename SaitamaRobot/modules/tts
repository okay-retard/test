from telegram import ChatAction
from gtts import gTTS
import html
import urllib.request
import re
import json
from datetime import datetime
from typing import Optional, List
import time
import requests
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown, mention_html
from SaitamaRobot import dispatcher
from SaitamaRobot.__main__ import STATS
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from SaitamaRobot.modules.helper_funcs.extraction import extract_user

def tts(update: Update, context: CallbackContext):
    args = context.args
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = " ".join(args)
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    lang="ml"
    tts = gTTS(reply, lang)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "en"
        tts = gTTs(reply, lang)
        tts.save("k.mp3")
    with open("k.mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)

dispatcher.add_handler(CommandHandler('tts', tts))

__help__ = """
*turns your text to audio format(beta phase)*
just do as follows:-
 -/tts <Any Text> : Converts text to speech.
"""
__mod_name__ = "tts"
