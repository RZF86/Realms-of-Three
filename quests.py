"""
Quest system with progressive difficulty and rewards
"""

import random


class Quest:
    """Base quest class"""
    
    def __init__(self, quest_id, name, description, difficulty, reward_gold, reward_exp, reward_item=None):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.difficulty = difficulty  # 1-5 stars
        self.reward_gold = reward_gold
        self.reward_exp = reward_exp
        self.reward_item = reward_item
        self.status = "available"  # available, in_progress, completed
        self.progress = 0
        self.required_progress = 1
        
    def get_difficulty_stars(self):
        """Get difficulty as stars"""
        return "⭐" * self.difficulty
    
    def get_reward_text(self):
        """Get formatted reward text"""
        text = f"{self.reward_gold}g + {self.reward_exp} EXP"
        if self.reward_item:
            text += f" + {self.reward_item}"
        return text


class KillQuest(Quest):
    """Quest to kill X enemies"""
    
    def __init__(self, quest_id, name, difficulty, enemies_to_kill):
        reward_gold = 100 * difficulty
        reward_exp = 200 * difficulty
        reward_item = None
        
        if difficulty >= 3:
            reward_item = "Rare Equipment"
        if difficulty >= 4:
            reward_item = "Legendary Equipment"
        
        super().__init__(
            quest_id, name,
            f"Defeat {enemies_to_kill} enemies",
            difficulty, reward_gold, reward_exp, reward_item
        )
        self.enemies_to_kill = enemies_to_kill
        self.enemies_killed = 0
        self.required_progress = enemies_to_kill
    
    def add_kill(self):
        """Add a kill to quest progress"""
        if self.status == "in_progress":
            self.enemies_killed += 1
            self.progress = self.enemies_killed
            
            if self.enemies_killed >= self.enemies_to_kill:
                self.status = "completed"
                return True
        return False


class BossQuest(Quest):
    """Quest to defeat a boss"""
    
    def __init__(self, quest_id, name, difficulty, boss_name):
        reward_gold = 500 * difficulty
        reward_exp = 1000 * difficulty
        reward_item = "Legendary Equipment" if difficulty >= 3 else None
        
        super().__init__(
            quest_id, name,
            f"Defeat {boss_name}",
            difficulty, reward_gold, reward_exp, reward_item
        )
        self.boss_name = boss_name
        self.boss_defeated = False
        self.required_progress = 1
    
    def defeat_boss(self):
        """Mark boss as defeated"""
        if self.status == "in_progress":
            self.boss_defeated = True
            self.progress = 1
            self.status = "completed"
            return True
        return False


class CollectQuest(Quest):
    """Quest to collect items or resources"""
    
    def __init__(self, quest_id, name, difficulty, item_name, amount):
        reward_gold = 150 * difficulty
        reward_exp = 300 * difficulty
        reward_item = "Gold Bonus" if difficulty >= 4 else None
        
        super().__init__(
            quest_id, name,
            f"Collect {amount} {item_name}",
            difficulty, reward_gold, reward_exp, reward_item
        )
        self.item_name = item_name
        self.amount_needed = amount
        self.amount_collected = 0
        self.required_progress = amount
    
    def add_item(self, count=1):
        """Add collected items"""
        if self.status == "in_progress":
            self.amount_collected += count
            self.progress = self.amount_collected
            
            if self.amount_collected >= self.amount_needed:
                self.status = "completed"
                return True
        return False


class SurvivalQuest(Quest):
    """Quest to survive for X seconds"""
    
    def __init__(self, quest_id, name, difficulty, duration_seconds):
        reward_gold = 200 * difficulty
        reward_exp = 400 * difficulty
        reward_item = "Rare Equipment" if difficulty >= 3 else None
        
        super().__init__(
            quest_id, name,
            f"Survive for {duration_seconds} seconds",
            difficulty, reward_gold, reward_exp, reward_item
        )
        self.duration_seconds = duration_seconds
        self.elapsed_seconds = 0
        self.required_progress = duration_seconds
    
    def update_time(self, delta_time):
        """Update survival time"""
        if self.status == "in_progress":
            self.elapsed_seconds += delta_time
            self.progress = int(self.elapsed_seconds)
            
            if self.elapsed_seconds >= self.duration_seconds:
                self.status = "completed"
                return True
        return False


class QuestManager:
    """Manages all quests for the player"""
    
    # Quest templates by difficulty
    easy_quests = [
        ("defeat_10_enemies", "Starter's Challenge", KillQuest, 1, 10),
        ("defeat_15_enemies", "Warm Up", KillQuest, 1, 15),
        ("survive_30_sec", "Quick Survivor", SurvivalQuest, 1, 30),
    ]
    
    medium_quests = [
        ("defeat_30_enemies", "Monster Hunter", KillQuest, 2, 30),
        ("defeat_50_enemies", "Slayer", KillQuest, 2, 50),
        ("mini_boss_1", "Mini Boss Takedown", BossQuest, 2, "Mini Boss"),
        ("survive_60_sec", "Endurance Test", SurvivalQuest, 2, 60),
    ]
    
    hard_quests = [
        ("defeat_100_enemies", "Elite Killer", KillQuest, 3, 100),
        ("defeat_boss_1", "Boss Slayer", BossQuest, 3, "Boss"),
        ("survive_120_sec", "Iron Skin", SurvivalQuest, 3, 120),
    ]
    
    nightmare_quests = [
        ("defeat_200_enemies", "Massacre", KillQuest, 4, 200),
        ("defeat_3_bosses", "Triple Threat", BossQuest, 4, "Boss"),
        ("survive_300_sec", "Immortal", SurvivalQuest, 4, 300),
    ]
    
    legendary_quests = [
        ("defeat_500_enemies", "Legendary Warrior", KillQuest, 5, 500),
        ("defeat_5_bosses", "Raid Master", BossQuest, 5, "Boss"),
        ("survive_600_sec", "Eternal Guardian", SurvivalQuest, 5, 600),
    ]
    
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []
        self.total_quests_completed = 0
        self.current_difficulty = 1
        self.quest_counter = 0
        
    def initialize_quests(self):
        """Initialize starting quests"""
        self.add_random_quest()
    
    def get_difficulty_tier(self, player_level):
        """Determine quest difficulty tier based on player level"""
        if player_level >= 40:
            return 5, self.legendary_quests
        elif player_level >= 30:
            return 4, self.nightmare_quests
        elif player_level >= 20:
            return 3, self.hard_quests
        elif player_level >= 10:
            return 2, self.medium_quests
        else:
            return 1, self.easy_quests
    
    def add_random_quest(self, player_level=1, max_active=3):
        """Add a random quest based on player level"""
        if len(self.active_quests) >= max_active:
            return False, "Maximum active quests reached!"
        
        difficulty, quest_pool = self.get_difficulty_tier(player_level)
        quest_template = random.choice(quest_pool)
        
        quest_id = f"{quest_template[0]}_{self.quest_counter}"
        self.quest_counter += 1
        
        if quest_template[2] == KillQuest:
            quest = KillQuest(quest_id, quest_template[1], difficulty, quest_template[4])
        elif quest_template[2] == BossQuest:
            quest = BossQuest(quest_id, quest_template[1], difficulty, quest_template[4])
        elif quest_template[2] == SurvivalQuest:
            quest = SurvivalQuest(quest_id, quest_template[1], difficulty, quest_template[4])
        else:
            return False, "Unknown quest type!"
        
        self.active_quests.append(quest)
        return True, f"New Quest Available: {quest.name}!"
    
    def start_quest(self, quest_index):
        """Start a quest"""
        if 0 <= quest_index < len(self.active_quests):
            quest = self.active_quests[quest_index]
            if quest.status == "available":
                quest.status = "in_progress"
                return True, f"Started Quest: {quest.name}"
        return False, "Cannot start quest!"
    
    def get_active_quests(self):
        """Get all active quests"""
        return [q for q in self.active_quests if q.status != "completed"]
    
    def get_completed_quests(self):
        """Get completed quests that haven't been claimed"""
        return [q for q in self.active_quests if q.status == "completed"]
    
    def claim_reward(self, quest_index):
        """Claim reward for completed quest"""
        if 0 <= quest_index < len(self.active_quests):
            quest = self.active_quests[quest_index]
            if quest.status == "completed":
                self.completed_quests.append(quest)
                self.active_quests.remove(quest)
                self.total_quests_completed += 1
                
                rewards = {
                    'gold': quest.reward_gold,
                    'exp': quest.reward_exp,
                    'item': quest.reward_item
                }
                return True, rewards
        return False, None
    
    def add_enemy_kill(self):
        """Track enemy kill for relevant quests"""
        completed = False
        for quest in self.get_active_quests():
            if isinstance(quest, KillQuest):
                if quest.add_kill():
                    completed = True
        return completed
    
    def add_boss_kill(self):
        """Track boss kill for relevant quests"""
        for quest in self.get_active_quests():
            if isinstance(quest, BossQuest):
                if quest.defeat_boss():
                    return True
        return False
    
    def update_survival_time(self, delta_time):
        """Update survival time for survival quests"""
        for quest in self.get_active_quests():
            if isinstance(quest, SurvivalQuest):
                if quest.update_time(delta_time):
                    return True
        return False
    
    def get_quest_progress_text(self, quest):
        """Get formatted progress text for a quest"""
        if isinstance(quest, KillQuest):
            return f"{quest.enemies_killed}/{quest.enemies_to_kill} enemies"
        elif isinstance(quest, BossQuest):
            return "Defeated!" if quest.boss_defeated else "In Progress..."
        elif isinstance(quest, SurvivalQuest):
            minutes = int(quest.elapsed_seconds) // 60
            seconds = int(quest.elapsed_seconds) % 60
            return f"{minutes}:{seconds:02d}/{int(quest.duration_seconds)//60}:{int(quest.duration_seconds)%60:02d}"
        return "Unknown"
