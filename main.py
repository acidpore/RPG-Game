# main.py
import tkinter as tk
import random
from tkinter import messagebox, ttk
from game.character import Character
from game.combat import CombatSystem, ENEMY_TEMPLATES
from game.inventory import InventorySystem

class RPGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python RPG")
        self.geometry("1024x768")
        
        self.player = None
        self.inventory_system = None
        self.current_enemy = None
        
        self.create_main_menu()
        
    def create_main_menu(self):
        """Main menu with new/load game options"""
        self.clear_window()
        
        tk.Label(self, text="Dragon Quest", font=("Arial", 24)).pack(pady=50)
        tk.Button(self, text="New Game", command=self.start_new_game, width=20).pack(pady=10)
        tk.Button(self, text="Load Game", state=tk.DISABLED, width=20).pack(pady=10)
        tk.Button(self, text="Exit", command=self.quit, width=20).pack(pady=10)

    def start_new_game(self):
        """Initialize new game state"""
        self.player = Character("Hero")
        self.inventory_system = InventorySystem(self.player)
        self.create_game_interface()
        self.update_character_display()
        
        # Add starter items
        self.inventory_system.add_item('small_heal', 3)
        self.inventory_system.add_item('iron_sword')

    def create_game_interface(self):
        """Create main game UI layout"""
        self.clear_window()
        
        # Left panel - Character info
        self.left_panel = tk.Frame(self, width=300, bg="#333")
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Character info labels
        self.char_labels = {}
        stats = ["name", "level", "health", "mana", "exp", "gold"]
        for stat in stats:
            self.char_labels[stat] = tk.Label(self.left_panel, bg="#333", fg="white")
            self.char_labels[stat].pack(pady=2, anchor="w")
        
        # Inventory button
        tk.Button(self.left_panel, text="Inventory", command=self.show_inventory).pack(pady=10)
        
        # Main game area
        self.main_area = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, bg="black", fg="white")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel - Actions
        self.right_panel = tk.Frame(self, width=300, bg="#333")
        self.right_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        # Combat buttons
        tk.Button(self.right_panel, text="Fight Goblin", 
                 command=lambda: self.start_combat("goblin")).pack(pady=5)
        tk.Button(self.right_panel, text="Fight Troll",
                 command=lambda: self.start_combat("troll")).pack(pady=5)

    def update_character_display(self):
        """Refresh character stats display"""
        stats = {
            "name": f"Name: {self.player.name}",
            "level": f"Level: {self.player.level}",
            "health": f"Health: {self.player.health}/{self.player.max_health}",
            "mana": f"Mana: {self.player.mana}/{self.player.max_mana}",
            "exp": f"EXP: {self.player.exp}/{self.player.exp_to_next}",
            "gold": f"Gold: {self.player.gold}"
        }
        
        for stat, text in stats.items():
            self.char_labels[stat].config(text=text)

    def start_combat(self, enemy_type):
        """Initiate combat sequence"""
        enemy = ENEMY_TEMPLATES[enemy_type]
        combat = CombatSystem(self.player, enemy)
        victory, message, log = combat.start_battle()
        
        # Display combat log
        self.main_area.config(state=tk.NORMAL)
        self.main_area.insert(tk.END, "\n=== BATTLE ===\n")
        for entry in log:
            self.main_area.insert(tk.END, entry + "\n")
        self.main_area.insert(tk.END, message + "\n")
        self.main_area.see(tk.END)
        self.main_area.config(state=tk.DISABLED)
        
        # Handle results
        if victory:
            # Add loot
            for item in enemy["loot"]:
                self.inventory_system.add_item(item)
            self.player.gold += random.randint(5, 20)
        
        self.update_character_display()
        self.check_game_over()

    def show_inventory(self):
        """Display inventory popup"""
        popup = tk.Toplevel(self)
        popup.title("Inventory")
        
        # Equipment slots
        tk.Label(popup, text="Equipped:").grid(row=0, column=0, sticky="w")
        for i, (slot, item) in enumerate(self.player.equipment.items()):
            tk.Label(popup, text=f"{slot.capitalize()}:").grid(row=i+1, column=0)
            tk.Label(popup, text=item.name if item else "Empty").grid(row=i+1, column=1)
        
        # Inventory items
        tk.Label(popup, text="Inventory:").grid(row=0, column=2, columnspan=2)
        for i, item in enumerate(self.inventory_system.items):
            tk.Label(popup, text=item.name).grid(row=i+1, column=2)
            
            if item.type == "consumable":
                btn = tk.Button(popup, text="Use", 
                              command=lambda i=i: self.use_inventory_item(i))
                btn.grid(row=i+1, column=3)
            elif item.type == "equipment":
                btn = tk.Button(popup, text="Equip", 
                              command=lambda i=i: self.equip_item(i))
                btn.grid(row=i+1, column=3)

    def use_inventory_item(self, index):
        """Use consumable item"""
        item = self.inventory_system.items[index]
        if self.inventory_system.use_item(item):
            self.update_character_display()
            self.show_inventory()
            
    def equip_item(self, index):
        """Equip equipment item"""
        item = self.inventory_system.items[index]
        if self.inventory_system.equip_item(item):
            self.update_character_display()
            self.show_inventory()

    def check_game_over(self):
        """Handle player death"""
        if self.player.health <= 0:
            messagebox.showinfo("Game Over", "You have been defeated!")
            self.create_main_menu()

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = RPGApp()
    app.mainloop()