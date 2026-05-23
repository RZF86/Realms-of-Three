"""
Shop system for buying and selling equipment
"""

class Shop:
    """Base shop class"""
    
    def __init__(self, name, level_requirement, discount=0):
        self.name = name
        self.level_requirement = level_requirement
        self.discount = discount  # 0-1, percentage discount on items
        self.weapons = []
        self.armor = []
        self.potions = []
        
    def get_discounted_price(self, base_price):
        """Get price with shop discount applied"""
        return int(base_price * (1 - self.discount))


class NoobShop(Shop):
    """Starter shop - available from the beginning"""
    
    def __init__(self):
        super().__init__("Noob Shop", 1, 0)
        self.description = "Welcome, adventurer! Here you'll find basic equipment to start your journey."
        
        # Weapons for sale (tuple: name, base_damage, crit_chance, attack_speed, rarity, price)
        self.weapons = [
            ('Wooden Sword', 8, 0.05, 1.0, 'common', 50),
            ('Iron Mace', 12, 0.08, 0.9, 'common', 60),
            ('Rusty Axe', 10, 0.10, 0.85, 'common', 55),
        ]
        
        # Armor for sale (tuple: name, base_defense, health_bonus, rarity, price)
        self.armor = [
            ('Leather Armor', 8, 20, 'common', 50),
            ('Cloth Robe', 5, 40, 'common', 40),
            ('Wooden Shield', 10, 15, 'common', 45),
        ]
        
        # Health potions (tuple: name, heal_amount, price)
        self.potions = [
            ('Minor Health Potion', 30, 20),
            ('Small Health Potion', 50, 35),
        ]


class ProShop(Shop):
    """Mid-game shop - available at level 10"""
    
    def __init__(self):
        super().__init__("Pro Shop", 10, 0.1)  # 10% discount
        self.description = "You've proven yourself! Here's some better equipment for seasoned adventurers."
        
        self.weapons = [
            ('Steel Sword', 18, 0.15, 0.95, 'uncommon', 120),
            ('Battle Hammer', 22, 0.08, 0.8, 'uncommon', 140),
            ('Enchanted Bow', 16, 0.25, 1.1, 'uncommon', 130),
            ('Dark Scythe', 20, 0.12, 0.85, 'uncommon', 135),
        ]
        
        self.armor = [
            ('Steel Plate', 20, 50, 'uncommon', 120),
            ('Mithril Vest', 18, 60, 'uncommon', 130),
            ('Dragon Scale Mail', 25, 45, 'uncommon', 150),
            ('Enchanted Robe', 12, 80, 'uncommon', 110),
        ]
        
        self.potions = [
            ('Health Potion', 80, 50),
            ('Greater Health Potion', 120, 75),
            ('Mana Potion', 50, 40),
        ]


class AceShop(Shop):
    """End-game shop - available at level 25"""
    
    def __init__(self):
        super().__init__("Ace Shop", 25, 0.2)  # 20% discount
        self.description = "Master adventurer! Here lies the ultimate equipment for true legends."
        
        self.weapons = [
            ('Mythril Blade', 35, 0.25, 1.05, 'rare', 250),
            ('Ancient Greatsword', 40, 0.18, 0.9, 'rare', 280),
            ('Celestial Staff', 32, 0.30, 1.2, 'rare', 260),
            ('Demon Reaper', 38, 0.22, 0.95, 'rare', 270),
            ('Holy Excalibur', 42, 0.20, 1.0, 'rare', 300),
        ]
        
        self.armor = [
            ('Adamantite Plate', 40, 100, 'rare', 250),
            ('Divine Armor', 38, 120, 'rare', 270),
            ('Shadow Cloak', 32, 140, 'rare', 260),
            ('Crystal Carapace', 45, 110, 'rare', 290),
            ('Eternal Guardian', 42, 130, 'rare', 300),
        ]
        
        self.potions = [
            ('Supreme Health Potion', 200, 100),
            ('Elixir of Life', 300, 150),
            ('Phoenix Feather Potion', 400, 200),
            ('Divine Blessing Potion', 250, 120),
        ]


class ShopManager:
    """Manages all shops in the game"""
    
    def __init__(self):
        self.shops = [
            NoobShop(),
            ProShop(),
            AceShop()
        ]
        self.current_shop = None
    
    def get_available_shops(self, player_level):
        """Get all shops available for the player's level"""
        available = []
        for shop in self.shops:
            if player_level >= shop.level_requirement:
                available.append(shop)
        return available
    
    def open_shop(self, shop_index, player_level):
        """Open a specific shop if player has access"""
        if 0 <= shop_index < len(self.shops):
            shop = self.shops[shop_index]
            if player_level >= shop.level_requirement:
                self.current_shop = shop
                return True, f"Welcome to {shop.name}!"
        return False, "You cannot access this shop yet!"
    
    def buy_weapon(self, weapon_index, player_gold):
        """Buy a weapon from current shop"""
        if not self.current_shop:
            return False, None, "No shop open!"
        
        if 0 <= weapon_index < len(self.current_shop.weapons):
            weapon_data = self.current_shop.weapons[weapon_index]
            price = self.current_shop.get_discounted_price(weapon_data[4])  # Use rarity as temp
            
            # Calculate actual price
            base_price = 100  # Base weapon price
            if weapon_data[4] == 'uncommon':
                base_price = 120
            elif weapon_data[4] == 'rare':
                base_price = 250
            
            price = self.current_shop.get_discounted_price(base_price)
            
            if player_gold >= price:
                weapon_info = {
                    'name': weapon_data[0],
                    'base_damage': weapon_data[1],
                    'crit_chance': weapon_data[2],
                    'attack_speed': weapon_data[3],
                    'rarity': weapon_data[4]
                }
                return True, weapon_info, f"Purchased {weapon_data[0]} for {price} gold!"
            else:
                needed = price - player_gold
                return False, None, f"Need {needed} more gold!"
        
        return False, None, "Item not found!"
    
    def buy_armor(self, armor_index, player_gold):
        """Buy armor from current shop"""
        if not self.current_shop:
            return False, None, "No shop open!"
        
        if 0 <= armor_index < len(self.current_shop.armor):
            armor_data = self.current_shop.armor[armor_index]
            
            # Calculate price based on rarity
            base_price = 100
            if armor_data[3] == 'uncommon':
                base_price = 120
            elif armor_data[3] == 'rare':
                base_price = 250
            
            price = self.current_shop.get_discounted_price(base_price)
            
            if player_gold >= price:
                armor_info = {
                    'name': armor_data[0],
                    'base_defense': armor_data[1],
                    'health_bonus': armor_data[2],
                    'rarity': armor_data[3]
                }
                return True, armor_info, f"Purchased {armor_data[0]} for {price} gold!"
            else:
                needed = price - player_gold
                return False, None, f"Need {needed} more gold!"
        
        return False, None, "Item not found!"
    
    def buy_potion(self, potion_index, player_gold):
        """Buy a potion from current shop"""
        if not self.current_shop:
            return False, None, "No shop open!"
        
        if 0 <= potion_index < len(self.current_shop.potions):
            potion_data = self.current_shop.potions[potion_index]
            price = potion_data[2]
            
            if player_gold >= price:
                potion_info = {
                    'name': potion_data[0],
                    'heal_amount': potion_data[1]
                }
                return True, potion_info, f"Purchased {potion_data[0]} for {price} gold!"
            else:
                needed = price - player_gold
                return False, None, f"Need {needed} more gold!"
        
        return False, None, "Item not found!"
    
    def get_shop_inventory(self):
        """Get current shop's inventory"""
        if self.current_shop:
            return {
                'name': self.current_shop.name,
                'description': self.current_shop.description,
                'weapons': self.current_shop.weapons,
                'armor': self.current_shop.armor,
                'potions': self.current_shop.potions,
                'discount': int(self.current_shop.discount * 100)
            }
        return None
