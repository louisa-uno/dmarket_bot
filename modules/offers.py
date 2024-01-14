import datetime
from typing import List
from db.crud import SelectSkinOffer, SkinOffer
from api.schemas import SellOffer, CreateOffer, CreateOffers, LastPrice, EditOffer, EditOffers, \
    DeleteOffers, DeleteOffer, OfferDetails
from api.dmarketapi import DMarketApi
from config import PUBLIC_KEY, SECRET_KEY, SellParams, logger, GAMES
from time import time


class History:
    def __init__(self, bot: DMarketApi):
        self.bot = bot

    @staticmethod
    def skins_db() -> List[SkinOffer]:
        skins = SelectSkinOffer.select_all()
        if skins:
            return [i for i in skins if not i.sellTime]
        return list()

    async def save_skins(self):
        logger.debug('Save skins')
        buy = await self.bot.closed_targets(limit='100')
        logger.debug(f"Buys: {len(buy.Trades)}")
        buy = buy.Trades
        logger.debug(f"Buy #1: {buy[0]}")
        logger.debug(f"Buys: {len(buy)}")
        buy = [SellOffer(OfferID=i.OfferID, TargetID=i.TargetID, AssetID=i.AssetID, buyPrice=float(i.Price.Amount), Amount=i.Amount) for i in buy]
        logger.debug("Sell offers created successfully")
        logger.debug(f"SellOffers: {len(buy)}")
        logger.debug(f"Buy #1: {buy[0]}")
        sold = []
        for game in GAMES:
            logger.debug(f"Game: {game}")
            sell = await self.bot.user_offers_closed(game=game, limit='100')
            sell = sell.Trades
            sold += sell
        logger.debug(f"Sells: {len(sold)}")
        sell = [SellOffer(AssetID=i.AssetID, OfferID=i.OfferID,
                        sellPrice=i.Price.Amount, sellTime=i.OfferClosedAt,
                        title=i.Title, game='rust') for i in sold]
        logger.debug(f"Sells: {len(sell)}")
        # for s in sell:
        #     logger.debug(f"sell: {s}")
        buy_asset_ids = [s.AssetID for s in SelectSkinOffer.select_all()]
        logger.debug(f"Buy asset ids: {len(buy_asset_ids)}")
        for b in buy:
            logger.debug(f"Buy: {b}")
            if b.AssetID not in buy_asset_ids:
                logger.debug(f"Adding skin: {b}")
                SelectSkinOffer.create_skin(b)
        skins = self.skins_db()
        logger.debug(f"Skins: {len(skins)}")

        for s in skins:
            for i in sell:
                # logger.debug(f"s.AssetID: {s.AssetID} i.AssetID: {i.AssetID}")
                # logger.debug(f"{s.AssetID == i.AssetID}")
                if s.AssetID == i.AssetID:
                    logger.debug(f"Skin: {s}")
                    s.title = i.title
                    s.sellPrice = i.sellPrice * (1 - s.fee / 100)
                    s.OfferID = i.OfferID
                    s.sellTime = i.sellTime
                    s.game = i.game
                    break
        SelectSkinOffer.update_sold(skins)


class Offers:
    def __init__(self, bot: DMarketApi):
        self.bot = bot
        self.max_percent = SellParams.MAX_PERCENT
        self.min_percent = SellParams.MIN_PERCENT

    async def add_to_sell(self):
        logger.debug('Add to sell')
        skins = SelectSkinOffer.select_not_sell()
        logger.debug(f'Add to sell (1/2) complete')
        logger.debug(f"First skin: {skins[0]}")
        # logger.debug(f'Skins: {len(skins)}')
        inv_skins = []
        invent = []
        for game in GAMES:
            logger.debug(f'Getting items for game: {game}')
            inv = await self.bot.user_items(game=game)
            inv_skins += inv.objects
        logger.debug(f'Add to sell (2/2) complete')
        logger.debug(f"First inv skin: {inv_skins[0]}\n\n")
        # logger.debug(f'Inv skins: {len(inv_skins)}')
        for i in inv_skins:
            fee = 7
            if 'custom' in i.fees['dmarket']['sell']:
                fee = int(i.fees['dmarket']['sell']['custom']['percentage'])
            if i.inMarket:
                invent.append(SellOffer(AssetID=i.itemId, title=i.title, game=i.gameId, fee=fee))
        logger.debug(f'Invent: {len(invent)}')
        for i in invent:
            logger.debug(f"i: {i}")
        create_offers = []
        for i in invent:
            for j in skins:
                if i.AssetID == j.AssetID:
                    price = j.buyPrice * (1 + self.max_percent / 100 + i.fee / 100)
                    i.sellPrice = price
            try:
                create_offers.append(CreateOffer(AssetID=i.AssetID,
                                                Price=LastPrice(Currency='USD', Amount=round(i.sellPrice, 2))))
            except TypeError:
                pass

        add = await self.bot.user_offers_create(CreateOffers(Offers=create_offers))
        if add.Result:
            for i in add.Result:
                for j in invent:
                    if i.CreateOffer.AssetID == j.AssetID:
                        j.sellPrice = i.CreateOffer.Price.Amount
                        j.OfferID = i.OfferID
                        SelectSkinOffer.update_offer_id(j)
        logger.debug(f'Add to sell: {add}')

    @staticmethod
    def offer_price(max_p, min_p, best) -> float:
        if best < min_p:
            order_price = min_p
        elif min_p < best <= max_p:
            order_price = best - 0.01
        else:
            order_price = max_p
        return order_price

    async def update_offers(self):
        logger.debug('Update offers')
        on_sale = sorted([i for i in SelectSkinOffer.select_not_sell() if i.OfferID],
                        key=lambda x: x.title)
        logger.debug(f'On sale: {len(on_sale)}')
        # names = [i.title for i in on_sell]
        # agr = await self.bot.agregated_prices(names=names, limit=len(names))
        items_to_update = list()
        for i in on_sale:
            item_id = OfferDetails(items=[i.AssetID])
            details = await self.bot.user_offers_details(body=item_id)
            best_price = details.objects[0].minListedPrice.amount / 100
            if i.sellPrice != best_price:
                max_sell_price = i.buyPrice * (1 + self.max_percent / 100 + i.fee / 100)
                min_sell_price = i.buyPrice * (1 + self.min_percent / 100 + i.fee / 100)
                price = self.offer_price(max_sell_price, min_sell_price, best_price)
                if round(price, 2) != round(i.sellPrice, 2):

                    i.sellPrice = price
                    items_to_update.append(EditOffer(OfferID=i.OfferID, AssetID=i.AssetID,
                                                    Price=LastPrice(Currency='USD', Amount=round(i.sellPrice, 2))))

        updated = await self.bot.user_offers_edit(EditOffers(Offers=items_to_update))
        for i in updated.Result:
            for j in on_sale:
                if i.EditOffer.AssetID == j.AssetID:
                    j.sellPrice = i.EditOffer.Price.Amount
                    j.OfferID = i.NewOfferID
                    logger.debug(f'{i.EditOffer.AssetID} {j.AssetID}')
                    SelectSkinOffer.update_offer_id(j)
        logger.debug(f'UPDATE OFFERS: {updated}')

    async def delete_all_offers(self):
        offers = await self.bot.user_offers(status='OfferStatusActive')
        do = [DeleteOffer(itemId=o.AssetID, offerId=o.Offer.OfferID, price=o.Offer.Price) for o in offers.Items]
        await self.bot.user_offers_delete(DeleteOffers(objects=do))
