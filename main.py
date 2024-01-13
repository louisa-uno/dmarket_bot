import asyncio

from api.dmarketapi import DMarketApi
from config import *
from modules.skinbase import SkinBase
from modules.orders import Orders
from modules.offers import History, Offers


bot = DMarketApi(PUBLIC_KEY, SECRET_KEY)
skin_base = SkinBase(bot)
orders = Orders(bot)
history = History(bot)
offers = Offers(bot)


async def create_pre_base():
    """Creating a primary database of items"""
    while True:
        logger.info('Skin database processing')
        try:
            await skin_base.update()
            logger.debug('Skin database sleep')
            await asyncio.sleep(skin_base.repeat)
        except Exception as e:
            logger.exception(f' Failed to update primary: {e}. Sleep for 5 seconds.')
            await asyncio.sleep(5)


async def orders_loop():
    await asyncio.sleep(5)
    while True:
        logger.debug(f'orders loop')
        try:
            logger.debug(f'{bot.balance}')
            if bot.balance > orders.order_list.min_price + BuyParams.STOP_ORDERS_BALANCE:
                await orders.update_orders()
                logger.debug(f'orders loop sleep')
                await asyncio.sleep(5)
            else:
                targets = await orders.bot.user_targets(limit='1000')
                targets_inactive = await orders.bot.user_targets(limit='1000', status='TargetStatusInactive')
                await orders.bot.delete_target(targets.Items + targets_inactive.Items)
                logger.debug('There is not enough balance available to place orders, we postpone analytics')
                await asyncio.sleep(60 * 5)
        except Exception as e:
            logger.error(f' Failed to update database of orders: {e}. Sleep for 5 seconds.')
            await asyncio.sleep(5)


async def history_loop():
    while True:
        logger.debug('History loop')
        try:
            await history.save_skins()
            logger.debug('History loop sleep')
            await asyncio.sleep(60*15)
        except Exception as e:
            logger.error(f' Failed to fetch history: {e}. Sleep for 30 seconds.')
            await asyncio.sleep(30)


async def add_to_sell_loop():
    while True:
        try:
            logger.debug('Add to sell loop')
            await offers.add_to_sell()
            logger.debug('Add to sell loop sleep')
            await asyncio.sleep(60*10)
        except Exception as e:
            logger.error(f' Failed to list skin/item for sale: {e}. Sleep for 30 seconds.')
            await asyncio.sleep(10)


async def update_offers_loop():
    while True:
        try:
            await offers.update_offers()
            logger.debug('Update offers loop sleep')
            await asyncio.sleep(60*15)
        except Exception as e:
            logger.error(f' Failed to update sellable skins/items: {e}. Sleep for 30 seconds.')
            await asyncio.sleep(30)


async def delete_offers_loop():
    while True:
        try:
            logger.debug('Delete offers loop sleep')
            await asyncio.sleep(60*60*24*2)
            logger.debug('Delete offers loop')
            await offers.delete_all_offers()
        except Exception as e:
            logger.error(f'Failed to delete offers: {e}')
            await asyncio.sleep(30)


async def main_loop():
    tasks = await asyncio.gather(
            bot.get_money_loop(),
            # delete_offers_loop(),
            history_loop(),
            # orders_loop(),
            add_to_sell_loop(),
            update_offers_loop(),
            create_pre_base(),
            return_exceptions=True
            )
    return tasks


def main():
    try:
        logger.info('The bot is launching')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_loop())
    except KeyboardInterrupt:
        asyncio.run(bot.close())
        logger.info('The bot is shutting down')


if __name__ == '__main__':
    main()
