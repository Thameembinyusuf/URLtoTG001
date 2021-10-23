from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from urllib.parse import quote_plus, unquote
import math
from helpers.download_from_url import download_file, get_size
from helpers.file_handler import send_to_transfersh_async, progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from helpers.display_progress import progress_for_pyrogram, humanbytes
import os
import time
import datetime
import aiohttp
import asyncio
import mimetypes
from helpers.tools import execute
from helpers.ffprobe import stream_creator
from helpers.thumbnail_video import thumb_creator

async def rna2(bot , u):
  
    if not u.reply_to_message:
        await u.reply_text(text=f"Please Reply To Audio Files !\n\nExample:\n**/rna | filename | title(optional) | artists(optional)**")
        return
    
    m = u.reply_to_message
    ft = m.document or m.audio
    fsize = get_size(ft.file_size)
    if m.video or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Please Reply To Audio Files !\n\nMimeType: {ft.mime_type}")
        return
    else:
        tempname = "Audio_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp3"
        if ft.file_name:
            oldname = ft.file_name
            oldname = oldname.replace('%40','@')
            oldname = oldname.replace('%25','_')
            oldname = oldname.replace(' ','_')
        else:
            oldname = "Audio_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp3"
    
    if ft.mime_type.startswith("audio/"):
        if not "|" in u.text:
            await m.reply_text(text=f"Try Again !\n\nExample:\n**/rna | filename | title(optional) | artists(optional)**")
            return
        else:
            args = u.text.split("|")
            if len(args) <= 1:
                await m.reply_text(text=f"Try Again !\n\nExample:\n**/rna | filename | title(optional) | artists(optional)**")
                return
            else:
                
                if len(args) == 2:
                  cmd, newname = u.text.split("|", 1)
                  newname = newname.strip()
                  
                  if ft.title:
                    newtitle = ft.title
                  else:
                    newtitle = " "
                  
                  if ft.performer:
                    newartist = ft.performer
                  else:
                    newartist = " "

                elif len(args) == 3:
                  cmd, newname, newtitle = u.text.split("|", 2)
                  newname = newname.strip()
                  newtitle = newtitle.strip()
                  
                  if ft.performer:
                    newartist = ft.performer
                  else:
                    newartist = " "

                elif len(args) == 4:
                  cmd, newname, newtitle, newartist = u.text.split("|", 3)
                  newname = newname.strip()
                  newtitle = newtitle.strip()
                  newartist = newartist.strip()

                else:
                  await m.reply_text(text=f"Try Again !\n\nExample:\n**/rna | filename | title(optional) | artists(optional)**")
                  return
                
                if os.path.splitext(newname)[1]:
                    await m.reply_text(text=f"Dont Type Extension !\n\nExample:\n**/rna | filename | title(optional) | artists(optional)**")
                    return
                else:
                    newname = newname + ".mp3"
                    #msg1 = await m.reply_text(text=f"Current Filename: `{oldname}` [{fsize}]\nNew Name: `{newname}`")
                    msg2 = await m.reply_text(text=f"⬇️ Trying To Download Audio")
                    #if not os.path.isdir(download_path):
                    #    os.mkdir(download_path)
                    c_time = time.time()
                    file_path = await bot.download_media(
                        m,
                        file_name=tempname,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "⬇️ Downloading Status ...",
                            msg2,
                            c_time
                        )
                    )
                    if not file_path:
                        #await msg1.delete()
                        await msg2.edit(f"❌ Download Failed !")
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        return
                    else:
                        try:
                            if ft.duration:
                              duration = ft.duration
                            else:
                              duration = 0
                              metadata = extractMetadata(createParser(file_path))
                              if metadata and metadata.has("duration"):
                                duration = metadata.get("duration").seconds
 
                            await msg2.edit(f"⬆️ Trying to Upload as Audio ...")
                            c_time = time.time()
                            await bot.send_audio(
                              chat_id=m.chat.id,
                              file_name=newname,
                              performer=newartist,
                              title=newtitle,
                              duration=duration,
                              audio=file_path,
                              caption=f"**Filename:** `{newname}`\n**Title:** `{newtitle}`\n**Artist(s):** `{newartist}`\n**Size:** {fsize}",
                              reply_to_message_id=m.message_id,
                              progress=progress_for_pyrogram,
                              progress_args=(
                                f"⬆️Uploading Status ...",
                                msg2,
                                c_time
                              )
                            )
                            #await msg1.delete()
                            await msg2.delete()
                            try:
                                os.remove(file_path)
                            except:
                                pass
                        except Exception as e:
                            #await msg1.delete()
                            await msg2.edit(f"❌ Uploading as Audio Failed **Error:**\n\n{e}\n\n{metadata}")
                            try:
                                os.remove(file_path)
                            except:
                                pass
    else:
        await m.reply_text(text=f"Please Reply To Audio Files !\n\nMimeType: {ft.mime_type}")
        return
