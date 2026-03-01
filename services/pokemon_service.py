"""Pokemon TCG Service - Manages Pokemon card pack opening"""
import random
import asyncio
from services.http_service import HttpService
from utils.logger import log


class PokemonService:
    """Service for fetching Pokemon TCG cards"""
    
    BASE_URL = "https://api.tcgdex.net/v2/en"
    
    def __init__(self):
        self.http_service = HttpService()
    
    POPULAR_SETS = [
        "swsh3",   # Darkness Ablaze
        "swsh1",   # Sword & Shield Base
        "swsh2",   # Rebel Clash
        "swsh4",   # Vivid Voltage
        "swsh5",   # Battle Styles
        "xy1",     # XY Base
        "base1",   # Base Set
        "base4",   # Base Set 2
    ]
    
    async def open_pack(self, pack_size: int = 10, set_id: str = None):
        try:
            if not set_id:
                set_id = random.choice(self.POPULAR_SETS)
            
            log.info(f"Fetching {pack_size} random cards from set '{set_id}'...")
            
            url = f"{self.BASE_URL}/sets/{set_id}"
            
            log.debug(f"Requesting: {url}")
            
            session = await self.http_service.get_session()
            async with session.get(url) as response:
                log.debug(f"Response status: {response.status}")
                if response.status == 200:
                    set_data = await response.json()
                    cards_list = set_data.get("cards", [])
                    log.debug(f"Got {len(cards_list)} cards from set '{set_data.get('name')}'")
                    
                    if cards_list and len(cards_list) > 0:
                        num_to_pick = min(pack_size, len(cards_list))
                        selected_cards = random.sample(cards_list, num_to_pick)
                        
                        cards = []
                        for card_data in selected_cards:
                            card_id = card_data.get("id")
                            card_url = f"{self.BASE_URL}/cards/{card_id}"
                            
                            async with session.get(card_url) as card_response:
                                if card_response.status == 200:
                                    full_card_data = await card_response.json()
                                    
                                    card = {
                                        "name": full_card_data.get("name", "Unknown"),
                                        "rarity": full_card_data.get("rarity", "Common"),
                                        "types": full_card_data.get("types", []),
                                        "hp": full_card_data.get("hp"),
                                        "image": full_card_data.get("image"),
                                        "image_large": full_card_data.get("image") + "/high.webp" if full_card_data.get("image") else None,
                                        "set": set_data.get("name", "Unknown Set"),
                                        "number": full_card_data.get("localId", "?"),
                                        "artist": full_card_data.get("illustrator", "Unknown"),
                                        "set_logo": set_data.get("logo"),
                                        "set_symbol": set_data.get("symbol")
                                    }
                                    cards.append(card)
                                    log.debug(f"✓ {card['name']} ({card['rarity']}) #{card['number']}")
                                else:
                                    log.warning(f"Failed to fetch full card data for {card_id}: {card_response.status}")
                        
                        cards.sort(key=lambda x: int(x.get("number", 0)) if x.get("number", "0").isdigit() else 999)
                        
                        set_info = {
                            "name": set_data.get("name"),
                            "id": set_data.get("id"),
                            "logo": set_data.get("logo"),
                            "symbol": set_data.get("symbol"),
                            "release_date": set_data.get("releaseDate"),
                            "card_count": set_data.get("cardCount", {}),
                            "serie": set_data.get("serie", {})
                        }
                        
                        log.success(f"Opened pack with {len(cards)} cards from {set_info['name']}")
                        return cards, set_info
                    else:
                        log.error("No cards found in set")
                        return [], {}
                else:
                    log.error(f"API returned status {response.status}")
                    return [], {}
            
        except Exception as e:
            log.error(f"Error opening pack: {type(e).__name__}: {str(e)}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            return [], {}
    
    def _get_rarity_value(self, rarity: str):
        """Get numeric value for rarity (for sorting)"""
        rarity_order = {
            "Common": 1,
            "Uncommon": 2,
            "Rare": 3,
            "Rare Holo": 4,
            "Rare Ultra": 5,
            "Rare Holo EX": 6,
            "Rare Holo GX": 7,
            "Rare Holo V": 8
        }
        return rarity_order.get(rarity, 0)
    
    async def search_card(self, query: str):
        try:
            url = f"{self.BASE_URL}/cards"
            
            session = await self.http_service.get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    cards_list = await response.json()
                    for card_id in cards_list:
                        if query.lower() in card_id.lower():
                            card_url = f"{self.BASE_URL}/cards/{card_id}"
                            async with session.get(card_url) as card_response:
                                if card_response.status == 200:
                                    card_data = await card_response.json()
                                    card = {
                                        "name": card_data.get("name"),
                                        "rarity": card_data.get("rarity"),
                                        "types": card_data.get("types", []),
                                        "hp": card_data.get("hp"),
                                        "image": card_data.get("image"),
                                        "image_large": card_data.get("image") + "/high.webp" if card_data.get("image") else None,
                                        "set": card_data.get("set", {}).get("name"),
                                        "number": card_data.get("localId"),
                                        "artist": card_data.get("illustrator")
                                    }
                                    return card
            
            return None
            
        except Exception as e:
            log.error(f"Error searching card: {e}")
            return None
    
    def get_rarity_emoji(self, rarity: str):
        """Get emoji representation for rarity"""
        if not rarity:
            return "⚪"
        
        rarity_lower = rarity.lower()
        
        emoji_map = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "rare holo": "✨",
            "rare ultra": "🌟",
            "rare holo ex": "💎",
            "rare holo gx": "👑",
            "rare holo v": "🏆",
            "rare holo vmax": "⭐",
            "rare rainbow": "🌈",
            "rare secret": "🔐",
            "promo": "🎁",
            "ultra rare": "🌟",
            "secret rare": "🔐",
            "amazing rare": "💫"
        }
        
        return emoji_map.get(rarity_lower, "🔵")  
    
    def get_type_emoji(self, pokemon_type: str):
        """Get emoji representation for Pokemon type"""
        if not pokemon_type:
            return "⚪"
        
        type_lower = pokemon_type.lower()
        
        type_emoji = {
            "fire": "🔥",
            "water": "💧",
            "grass": "🌿",
            "electric": "⚡",
            "psychic": "🔮",
            "fighting": "👊",
            "darkness": "🌑",
            "metal": "⚙️",
            "fairy": "🧚",
            "dragon": "🐉",
            "colorless": "⚪",
            "lightning": "⚡",
            "normal": "⚪",
            "trainer": "🎯",
            "energy": "⚡"
        }
        return type_emoji.get(type_lower, "⚪")
