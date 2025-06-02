import asyncio

from providers import FlipFlatDataProvider


async def init_ff():
    await FlipFlatDataProvider().initialize()
    # from main import dump_flats_from_provider
    # await dump_flats_from_provider(FlipFlatDataProvider.provider_name, limit=10)


asyncio.run(init_ff())
