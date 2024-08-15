from typing import Optional

from sqlmodel import Session, select
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, Channel

from constants import Districts
from db import engine, create_db_and_tables
from models import Flat, UpdateLog
from utils import parse_message

from config import settings


def get_client() -> TelegramClient:
    return TelegramClient('anon', settings.app_id, settings.api_hash)


async def aget_client() -> TelegramClient:
    async with get_client() as client:
        yield client


async def get_channel(client: TelegramClient | None) -> Channel:
    if settings.tg_channel_id:
        return await client.get_entity(PeerChannel(settings.tg_channel_id))
    elif settings.tg_channel_name:
        return await client.get_entity(f't.me/{settings.tg_channel_name}')


async def dump_flats(client: TelegramClient, channel: Channel,
                     district: Districts | str, limit: Optional[int] = 100) -> int:
    with Session(engine) as session:
        last_message_id = session.exec(
            select(Flat.ff_id).where(
                Flat.district == district
            ).order_by(
                Flat.ff_id.desc()
            )
        ).first()
        last_message_id = last_message_id or 0
        n = 0
        async for message in client.iter_messages(channel, search=f'#{district}', min_id=last_message_id, limit=limit):
            f = Flat(
                ff_id=message.id,
                created_at=message.date,
                edit_date=message.edit_date,
                link_to_post=f'https://t.me/{channel.username}/{message.id}',
                original_text=message.text,
                district=district.lower()
            )
            parse_message(message.text, flat_object=f)
            session.add(f)
            session.commit()
            n += 1
        update_log = UpdateLog(
            district=district,
            number_of_flats=n
        )
        session.add(update_log)
        session.commit()
    return n


async def main(client: TelegramClient):
    channel = await get_channel(client)
    for district in list(Districts):
        await dump_flats(client, channel, district, limit=settings.max_posts_per_task)


if __name__ == '__main__':
    create_db_and_tables()
    c = get_client()
    with c:
        c.loop.run_until_complete(main(c))
