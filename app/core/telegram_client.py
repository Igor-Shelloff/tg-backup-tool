import asyncio
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, FloodWaitError, PhoneCodeInvalidError,
)
from telethon.tl.functions.channels import (
    CreateChannelRequest, EditPhotoRequest, GetFullChannelRequest,
)
from telethon.tl.functions.messages import EditChatAboutRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from app.config import SESSIONS_DIR


class TelegramBackupClient:
    def __init__(self, app):
        self.app = app
        self.client = None
        self.is_connected = False
        self.loop = asyncio.new_event_loop()
        self._code_event = threading.Event()
        self._password_event = threading.Event()
        self._code = None
        self._password = None
        self._stop_flag = threading.Event()
        self._qr_login = None

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run(self, coro, callback=None):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        if callback:
            def _done(f):
                try:
                    result = f.result()
                except Exception as e:
                    result = (False, str(e))
                self.app.root.after(0, lambda: callback(result))
            future.add_done_callback(_done)
        return future

    def is_authorized(self):
        if not self.client:
            return False
        try:
            return self.client.is_connected() and self.is_connected
        except Exception:
            return False

    async def _connect(self, api_id, api_hash, session_name):
        session_path = str(SESSIONS_DIR / session_name)
        if self.client and self.client.is_connected():
            try:
                await self.client.disconnect()
            except Exception:
                pass
        self.client = TelegramClient(session_path, api_id, api_hash)
        await self.client.connect()
        self.is_connected = True

    async def _authorize_phone(self, api_id, api_hash, phone, session_name):
        try:
            await self._connect(api_id, api_hash, session_name)

            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                return True, self._format_me(me)

            await self.client.send_code_request(phone)

            self._code_event.clear()
            self._code = None
            self.app.root.after(0, self.app.show_code_input)
            self._code_event.wait(timeout=300)

            code = self._code
            if not code:
                return False, "Code not entered"

            try:
                await self.client.sign_in(phone, code)
            except SessionPasswordNeededError:
                self._password_event.clear()
                self._password = None
                self.app.root.after(0, self.app.show_password_input)
                self._password_event.wait(timeout=300)

                password = self._password
                if not password:
                    return False, "Password not entered"
                await self.client.sign_in(password=password)

            me = await self.client.get_me()
            return True, self._format_me(me)
        except PhoneCodeInvalidError:
            return False, "Invalid code"
        except Exception as e:
            return False, str(e)

    async def _prompt_password(self):
        self._password_event.clear()
        self._password = None
        self.app.root.after(0, self.app.show_password_input)
        self._password_event.wait(timeout=300)
        return self._password

    async def _authorize_qr(self, api_id, api_hash, session_name):
        try:
            await self._connect(api_id, api_hash, session_name)

            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                return True, self._format_me(me)

            qr_login = await self.client.qr_login()
            self._qr_login = qr_login

            self.app.root.after(0, lambda: self.app.show_qr_code(qr_login.url))

            try:
                await qr_login.wait(timeout=180)
            except asyncio.TimeoutError:
                return False, "QR expired"
            except SessionPasswordNeededError:
                self.app.root.after(0, self.app.close_qr_window)

                password = await self._prompt_password()
                if not password:
                    return False, "Password not entered"

                await self.client.sign_in(password=password)

            me = await self.client.get_me()
            return True, self._format_me(me)
        except SessionPasswordNeededError:
            password = await self._prompt_password()
            if not password:
                return False, "Password not entered"
            try:
                await self.client.sign_in(password=password)
                me = await self.client.get_me()
                return True, self._format_me(me)
            except Exception as e:
                return False, str(e)
        except Exception as e:
            return False, str(e)

    async def _logout(self):
        try:
            if self.client and self.client.is_connected():
                await self.client.log_out()
        except Exception:
            pass
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
        except Exception:
            pass
        self.is_connected = False
        self.client = None

    @staticmethod
    def _format_me(me):
        first = getattr(me, "first_name", "") or ""
        last = getattr(me, "last_name", "") or ""
        username = getattr(me, "username", "") or ""
        name = (first + " " + last).strip() or "Unknown"
        if username:
            return f"{name} (@{username})"
        return name

    def authorize_phone(self, api_id, api_hash, phone, session_name, callback):
        self._run(
            self._authorize_phone(api_id, api_hash, phone, session_name),
            callback,
        )

    def authorize_qr(self, api_id, api_hash, session_name, callback):
        self._run(
            self._authorize_qr(api_id, api_hash, session_name),
            callback,
        )

    def submit_code(self, code):
        self._code = code
        self._code_event.set()

    def submit_password(self, password):
        self._password = password
        self._password_event.set()

    def logout(self, callback=None):
        self._run(self._logout(), callback)

    async def _get_channels(self):
        if not self.client or not self.is_connected:
            return []
        channels = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel:
                    channels.append({
                        "id": dialog.id,
                        "name": dialog.name,
                        "username": getattr(dialog.entity, "username", None),
                    })
        except Exception:
            pass
        return channels

    def get_channels(self, callback):
        self._run(self._get_channels(), callback)

    async def _export_channel(self, channel_id, export_path, options, on_progress):
        try:
            entity = await self.client.get_entity(channel_id)
            export_path = Path(export_path)
            media_dir = export_path / "media"
            media_dir.mkdir(parents=True, exist_ok=True)

            data = {
                "export_date": datetime.now().isoformat(),
                "channel_info": {},
                "messages": [],
            }

            if options.get("export_name", True):
                data["channel_info"]["title"] = entity.title

            if options.get("export_description", True):
                try:
                    full = await self.client(GetFullChannelRequest(channel=entity))
                    about = getattr(full.full_chat, "about", None)
                    if about and about.strip():
                        data["channel_info"]["description"] = about
                except Exception:
                    pass

            if options.get("export_avatar", True):
                try:
                    avatar_path = media_dir / "avatar.jpg"
                    result = await self.client.download_profile_photo(
                        entity, file=str(avatar_path)
                    )
                    if result:
                        data["channel_info"]["avatar"] = "media/avatar.jpg"
                except Exception:
                    pass

            if options.get("export_messages", True):
                limit = options.get("limit_messages", 0) or None
                count = 0
                async for message in self.client.iter_messages(entity, limit=limit):
                    if self._stop_flag.is_set():
                        break

                    msg = {
                        "id": message.id,
                        "date": message.date.isoformat() if message.date else None,
                        "text": message.text or "",
                        "media": None,
                        "media_type": None,
                    }

                    if options.get("export_media", True) and message.media:
                        try:
                            saved = await self._save_media(message, media_dir)
                            if saved:
                                msg["media"] = f"media/{saved}"
                                msg["media_type"] = "media"
                        except Exception:
                            pass

                    data["messages"].append(msg)
                    count += 1
                    if count % 10 == 0:
                        on_progress(count)

                data["total_messages"] = count

            json_path = export_path / "channel_data.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "path": str(export_path),
                "messages": len(data["messages"]),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _save_media(self, message, media_dir):
        media = message.media
        if isinstance(media, MessageMediaPhoto):
            filename = f"photo_{message.id}.jpg"
        elif isinstance(media, MessageMediaDocument):
            filename = None
            doc = media.document
            if doc and hasattr(doc, "attributes"):
                for attr in doc.attributes:
                    if hasattr(attr, "file_name") and attr.file_name:
                        filename = attr.file_name
                        break
            if not filename:
                mime = getattr(doc, "mime_type", "") if doc else ""
                ext = ".bin"
                if "image" in mime:
                    ext = ".jpg"
                elif "video" in mime:
                    ext = ".mp4"
                elif "audio" in mime:
                    ext = ".mp3"
                filename = f"document_{message.id}{ext}"
        else:
            return None

        file_path = media_dir / filename
        await self.client.download_media(message.media, file=str(file_path))
        return filename

    def export_channel(self, channel_id, export_path, options, on_progress, callback):
        self._stop_flag.clear()

        def _progress(count):
            self.app.root.after(0, lambda: on_progress(count))

        def _cb(result):
            self._stop_flag.clear()
            callback(result)

        self._run(self._export_channel(channel_id, export_path, options, _progress), _cb)

    def stop_export(self):
        self._stop_flag.set()

    async def _import_channel(self, backup_path, options, on_progress):
        try:
            backup_path = Path(backup_path)
            json_path = backup_path / "channel_data.json"
            if not json_path.exists():
                return {"success": False, "error": "channel_data.json not found"}

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            info = data.get("channel_info", {})
            messages = data.get("messages", [])

            title = options.get("new_channel_name") or info.get("title") or "Restored"
            about = info.get("description", "") if options.get("import_description", True) else ""

            result = await self.client(CreateChannelRequest(
                title=title, about=about, megagroup=False,
            ))
            new_channel = result.chats[0]

            if about:
                try:
                    await asyncio.sleep(1)
                    await self.client(EditChatAboutRequest(
                        peer=new_channel, about=about,
                    ))
                except Exception:
                    pass

            if options.get("import_avatar", True) and info.get("avatar"):
                avatar_path = backup_path / info["avatar"]
                if avatar_path.exists():
                    try:
                        uploaded = await self.client.upload_file(str(avatar_path))
                        await self.client(EditPhotoRequest(
                            channel=new_channel, photo=uploaded,
                        ))
                    except Exception:
                        pass

            imported = 0
            delay = float(options.get("delay", 1.0))

            if options.get("import_messages", True):
                sorted_msgs = sorted(messages, key=lambda m: m.get("date") or "")
                total = len(sorted_msgs)

                for i, m in enumerate(sorted_msgs):
                    if self._stop_flag.is_set():
                        break

                    text = m.get("text") or ""
                    media_file = None

                    if options.get("import_media", True) and m.get("media"):
                        media_path = backup_path / m["media"]
                        if media_path.exists():
                            try:
                                media_file = await self.client.upload_file(str(media_path))
                            except Exception:
                                media_file = None

                    try:
                        if media_file:
                            await self.client.send_file(
                                new_channel, media_file, caption=text,
                            )
                        elif text.strip():
                            await self.client.send_message(new_channel, text)
                        else:
                            continue

                        imported += 1
                        if imported % 5 == 0:
                            on_progress(imported, total)
                        await asyncio.sleep(delay)
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds)

            return {"success": True, "imported": imported, "channel_id": new_channel.id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def import_channel(self, backup_path, options, on_progress, callback):
        self._stop_flag.clear()

        def _progress(cur, total):
            self.app.root.after(0, lambda: on_progress(cur, total))

        def _cb(result):
            self._stop_flag.clear()
            callback(result)

        self._run(self._import_channel(backup_path, options, _progress), _cb)

    def stop_import(self):
        self._stop_flag.set()

    def disconnect(self):
        try:
            if self.client and self.client.is_connected():
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
        except Exception:
            pass