import pygame
import sys
import random
import math
import json
from typing import List, Dict, Any, Optional, Tuple

pygame.init()

WIDTH, HEIGHT = 1200, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
UI_BG = (40, 44, 52)
UI_ACCENT = (97, 175, 239)
UI_SECONDARY = (86, 182, 194)
UI_WARNING = (229, 192, 123)
UI_DANGER = (198, 120, 221)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚡ ЭлектроКвест - Виртуальная лаборатория")
clock = pygame.time.Clock()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(self.life * 255)
        size = int(self.life * 5)
        color_with_alpha = (*self.color, alpha)
        surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color_with_alpha, (size, size), size)
        screen.blit(surf, (self.x - size, self.y - size))

class Component:
    def __init__(self, x, y, resistance=0, voltage=0):
        self.x = x
        self.y = y
        self.resistance = resistance
        self.voltage = voltage
        self.current = 0
        self.connected_to = []
        self.connections = []
        self.is_selected = False
        self.is_burned = False
        self.max_power = float('inf')
        self.particles = []
        self.temperature = 0
        self.max_temperature = 100
        self.heat_color = (255, 255, 255)
        self.rect = pygame.Rect(x - 30, y - 30, 60, 60)
        self.voltage_drop = 0
        self.node_potentials = {}
    
    def add_connection_point(self, x, y):
        self.connections.append((x, y))
    
    def get_connection_points(self):
        return [(self.x + dx, self.y + dy) for dx, dy in self.connections]
    
    def connect(self, other_component):
        if other_component is None or other_component == self:
            return False
        
        if other_component not in self.connected_to:
            self.connected_to.append(other_component)
        
        if self not in other_component.connected_to:
            other_component.connected_to.append(self)
        
        return True
    
    def disconnect(self, other_component):
        if other_component in self.connected_to:
            self.connected_to.remove(other_component)
        if self in other_component.connected_to:
            other_component.connected_to.remove(self)
    
    def calculate_power(self):
        return abs(self.current) ** 2 * self.resistance
    
    def check_burn(self):
        power = self.calculate_power()
        if not self.is_burned and power > self.max_power:
            self.is_burned = True
            self.resistance = 1e9
            for _ in range(20):
                self.particles.append(Particle(self.x, self.y, (255, 255, 0)))
            return True
        return False
    
    def update_heat_effect(self):
        power = self.calculate_power()
        self.temperature = min(power * 10, self.max_temperature)
        heat_intensity = min(255, int(self.temperature * 2.55))
        self.heat_color = (255, 255 - heat_intensity, 255 - heat_intensity)
        return self.temperature
    
    def draw_heat_glow(self, screen):
        if self.temperature > 20:
            glow_radius = int(self.temperature / 5)
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            glow_alpha = min(150, int(self.temperature * 1.5))
            glow_color = (*self.heat_color[:3], glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
    
    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw_particles(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class Resistor(Component):
    def __init__(self, x, y, resistance=100):
        super().__init__(x, y, resistance)
        self.max_power = 1.2
        self.add_connection_point(-30, 0)
        self.add_connection_point(30, 0)
        self.color_stripes = self.generate_stripes()
        self.rect = pygame.Rect(x - 35, y - 20, 70, 40)
    
    def generate_stripes(self):
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), 
                 (0, 0, 255), (128, 0, 128)]
        return random.sample(colors, 4)
    
    def draw(self, screen):
        self.update_particles()
        self.update_heat_effect()
        
        if self.is_selected:
            pygame.draw.rect(screen, UI_ACCENT, (self.x - 35, self.y - 20, 70, 40), 3, border_radius=8)
        
        body_color = self.heat_color if self.temperature > 0 else (210, 180, 140)
        if self.is_burned:
            body_color = (100, 100, 100)
        
        pygame.draw.rect(screen, body_color, (self.x - 25, self.y - 10, 50, 20), border_radius=4)
        
        if not self.is_burned:
            for i, color in enumerate(self.color_stripes):
                pygame.draw.rect(screen, color, (self.x - 20 + i*10, self.y - 10, 6, 20))
        
        pygame.draw.line(screen, BLACK, (self.x - 35, self.y), (self.x - 25, self.y), 3)
        pygame.draw.line(screen, BLACK, (self.x + 25, self.y), (self.x + 35, self.y), 3)
        
        font = pygame.font.SysFont('arial', 14)
        if self.is_burned:
            text = font.render("ПЕРЕГОРЕЛ!", True, RED)
        else:
            text = font.render(f"{self.resistance}Ω", True, BLUE)
        screen.blit(text, (self.x - 20, self.y - 30))
        
        info_font = pygame.font.SysFont('arial', 10)
        current_text = info_font.render(f"I={abs(self.current):.2f}A", True, GREEN)
        voltage_text = info_font.render(f"U={abs(self.voltage_drop):.2f}V", True, RED)
        screen.blit(current_text, (self.x - 15, self.y + 15))
        screen.blit(voltage_text, (self.x - 15, self.y + 30))
        
        self.draw_heat_glow(screen)
        self.draw_particles(screen)

class Battery(Component):
    def __init__(self, x, y, voltage=9):
        super().__init__(x, y, 0.5, voltage)
        self.max_power = 200.0
        self.add_connection_point(-35, 0)
        self.add_connection_point(35, 0)
        self.charge_level = 1.0
        self.rect = pygame.Rect(x - 40, y - 25, 80, 50)
        self.positive_terminal = (self.x + 35, self.y)
        self.negative_terminal = (self.x - 35, self.y)
    
    def draw(self, screen):
        self.update_particles()
        self.update_heat_effect()
        
        if self.is_selected:
            pygame.draw.rect(screen, UI_ACCENT, (self.x - 40, self.y - 25, 80, 50), 3, border_radius=8)
        
        case_color = self.heat_color if self.temperature > 0 else (150, 150, 150)
        pygame.draw.rect(screen, case_color, (self.x - 30, self.y - 15, 60, 30), border_radius=4)
        
        if not self.is_burned:
            charge_color = GREEN if self.charge_level > 0.3 else YELLOW if self.charge_level > 0.1 else RED
            charge_width = 54 * self.charge_level
            pygame.draw.rect(screen, charge_color, (self.x - 27, self.y - 12, charge_width, 24))
        
        pygame.draw.rect(screen, RED, (self.x + 25, self.y - 20, 10, 8))
        pygame.draw.rect(screen, BLACK, (self.x - 35, self.y - 20, 10, 8))
        
        font = pygame.font.SysFont('arial', 14)
        text = font.render(f"{self.voltage}V", True, BLUE)
        screen.blit(text, (self.x - 15, self.y - 35))
        
        info_font = pygame.font.SysFont('arial', 10)
        current_text = info_font.render(f"I={abs(self.current):.2f}A", True, GREEN)
        screen.blit(current_text, (self.x - 15, self.y + 35))
        
        self.draw_heat_glow(screen)
        self.draw_particles(screen)

class Lamp(Component):
    def __init__(self, x, y, resistance=50):
        super().__init__(x, y, resistance)
        self.max_power = 2.0
        self.add_connection_point(-25, 0)
        self.add_connection_point(25, 0)
        self.is_lit = False
        self.brightness = 0
        self.rect = pygame.Rect(x - 35, y - 35, 70, 70)
    
    def draw(self, screen):
        self.update_particles()
        self.update_heat_effect()
        
        if self.is_selected:
            pygame.draw.circle(screen, UI_ACCENT, (self.x, self.y), 35, 3)
        
        self.is_lit = abs(self.current) > 0.001 and not self.is_burned
        target_brightness = 1.0 if self.is_lit else 0.0
        self.brightness += (target_brightness - self.brightness) * 0.2
        
        if self.brightness > 0.1:
            glow_size = int(40 * self.brightness)
            glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            glow_color = (255, 255, 200, int(128 * self.brightness))
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
        
        if self.is_burned:
            bulb_color = (100, 100, 100)
            filament_color = (50, 50, 50)
        else:
            intensity = int(200 + 55 * self.brightness)
            bulb_color = (intensity, intensity, 200)
            filament_color = (255, int(100 + 155 * self.brightness), 0)
        
        pygame.draw.circle(screen, bulb_color, (self.x, self.y), 25)
        pygame.draw.circle(screen, (100, 100, 100), (self.x, self.y), 25, 2)
        pygame.draw.line(screen, filament_color, (self.x - 10, self.y), (self.x + 10, self.y), 3)
        pygame.draw.rect(screen, (120, 120, 120), (self.x - 15, self.y + 20, 30, 8))
        pygame.draw.line(screen, BLACK, (self.x - 30, self.y), (self.x - 25, self.y), 3)
        pygame.draw.line(screen, BLACK, (self.x + 25, self.y), (self.x + 30, self.y), 3)
        
        info_font = pygame.font.SysFont('arial', 10)
        current_text = info_font.render(f"I={abs(self.current):.2f}A", True, GREEN)
        voltage_text = info_font.render(f"U={abs(self.voltage_drop):.2f}V", True, RED)
        power_text = info_font.render(f"P={self.calculate_power():.2f}W", True, ORANGE)
        screen.blit(current_text, (self.x - 15, self.y - 50))
        screen.blit(voltage_text, (self.x - 15, self.y - 65))
        screen.blit(power_text, (self.x - 15, self.y - 80))
        
        self.draw_heat_glow(screen)
        self.draw_particles(screen)

class Ammeter(Component):
    def __init__(self, x, y, resistance=0.01):
        super().__init__(x, y, resistance)
        self.max_power = 0.1
        self.add_connection_point(-25, 0)
        self.add_connection_point(25, 0)
        self.measured_current = 0
        self.needle_angle = math.pi
        self.rect = pygame.Rect(x - 30, y - 20, 60, 40)
    
    def update_needle(self):
        target_angle = math.pi + (abs(self.measured_current) / 1.0) * math.pi
        if target_angle > 2 * math.pi:
            target_angle = 2 * math.pi
        
        angle_diff = target_angle - self.needle_angle
        self.needle_angle += angle_diff * 0.1
    
    def draw(self, screen):
        self.update_particles()
        self.update_needle()
        
        if self.is_selected:
            pygame.draw.rect(screen, UI_ACCENT, (self.x - 35, self.y - 25, 70, 50), 3, border_radius=8)
        
        pygame.draw.rect(screen, (200, 200, 200), (self.x - 25, self.y - 15, 50, 30), border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), (self.x - 25, self.y - 15, 50, 30), 2, border_radius=5)
        
        pygame.draw.arc(screen, BLACK, (self.x - 15, self.y - 10, 30, 30), math.pi, 2 * math.pi, 2)
        
        for i in range(6):
            angle = math.pi + (i / 5) * math.pi
            start_x = self.x + 12 * math.cos(angle)
            start_y = self.y - 5 + 12 * math.sin(angle)
            end_x = self.x + 15 * math.cos(angle)
            end_y = self.y - 5 + 15 * math.sin(angle)
            pygame.draw.line(screen, BLACK, (start_x, start_y), (end_x, end_y), 1)
        
        end_x = self.x + 12 * math.cos(self.needle_angle)
        end_y = self.y - 5 + 12 * math.sin(self.needle_angle)
        pygame.draw.line(screen, RED, (self.x, self.y - 5), (end_x, end_y), 2)
        
        pygame.draw.rect(screen, (50, 50, 50), (self.x - 20, self.y + 8, 40, 12))
        font = pygame.font.SysFont('arial', 10)
        current_text = font.render(f"{self.measured_current:.2f}A", True, GREEN)
        screen.blit(current_text, (self.x - 18, self.y + 10))
        
        pygame.draw.line(screen, BLACK, (self.x - 30, self.y), (self.x - 25, self.y), 3)
        pygame.draw.line(screen, BLACK, (self.x + 25, self.y), (self.x + 30, self.y), 3)
        
        self.draw_particles(screen)

class Voltmeter(Component):
    def __init__(self, x, y, resistance=1e6):
        super().__init__(x, y, resistance)
        self.max_power = 0.001
        self.add_connection_point(-25, 0)
        self.add_connection_point(25, 0)
        self.measured_voltage = 0
        self.needle_angle = math.pi
        self.rect = pygame.Rect(x - 30, y - 20, 60, 40)
        self.measurement_points = []
    
    def update_needle(self):
        target_angle = math.pi + (abs(self.measured_voltage) / 10.0) * math.pi
        if target_angle > 2 * math.pi:
            target_angle = 2 * math.pi
        
        angle_diff = target_angle - self.needle_angle
        self.needle_angle += angle_diff * 0.1
    
    def draw(self, screen):
        self.update_particles()
        self.update_needle()
        
        if self.is_selected:
            pygame.draw.rect(screen, UI_ACCENT, (self.x - 35, self.y - 25, 70, 50), 3, border_radius=8)
        
        pygame.draw.rect(screen, (200, 200, 255), (self.x - 25, self.y - 15, 50, 30), border_radius=5)
        pygame.draw.rect(screen, (100, 100, 150), (self.x - 25, self.y - 15, 50, 30), 2, border_radius=5)
        
        pygame.draw.arc(screen, BLACK, (self.x - 15, self.y - 10, 30, 30), math.pi, 2 * math.pi, 2)
        
        for i in range(6):
            angle = math.pi + (i / 5) * math.pi
            start_x = self.x + 12 * math.cos(angle)
            start_y = self.y - 5 + 12 * math.sin(angle)
            end_x = self.x + 15 * math.cos(angle)
            end_y = self.y - 5 + 15 * math.sin(angle)
            pygame.draw.line(screen, BLACK, (start_x, start_y), (end_x, end_y), 1)
        
        end_x = self.x + 12 * math.cos(self.needle_angle)
        end_y = self.y - 5 + 12 * math.sin(self.needle_angle)
        pygame.draw.line(screen, RED, (self.x, self.y - 5), (end_x, end_y), 2)
        
        pygame.draw.rect(screen, (50, 50, 50), (self.x - 20, self.y + 8, 40, 12))
        font = pygame.font.SysFont('arial', 10)
        voltage_text = font.render(f"{self.measured_voltage:.2f}V", True, GREEN)
        screen.blit(voltage_text, (self.x - 18, self.y + 10))
        
        pygame.draw.line(screen, BLACK, (self.x - 30, self.y), (self.x - 25, self.y), 3)
        pygame.draw.line(screen, BLACK, (self.x + 25, self.y), (self.x + 30, self.y), 3)
        
        self.draw_particles(screen)

class Wire:
    def __init__(self, start_point, end_point, start_comp, end_comp):
        self.start_point = start_point
        self.end_point = end_point
        self.start_component = start_comp
        self.end_component = end_comp
        self.resistance = 0.001
        self.current = 0
    
    def draw(self, screen):
        if abs(self.current) > 0.001:
            intensity = min(255, 100 + int(abs(self.current) * 100))
            line_color = (intensity, intensity, 100)
        else:
            line_color = BLACK
        
        pygame.draw.line(screen, line_color, self.start_point, self.end_point, 4)
        
        if abs(self.current) > 0.01:
            t = pygame.time.get_ticks() / 200
            dx = self.end_point[0] - self.start_point[0]
            dy = self.end_point[1] - self.start_point[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                dx /= length
                dy /= length
                
                for i in range(3):
                    pos = (t * 50 + i * length/3) % length
                    x = self.start_point[0] + dx * pos
                    y = self.start_point[1] + dy * pos
                    
                    if 0 <= pos <= length:
                        charge_color = YELLOW if self.current > 0 else BLUE
                        pygame.draw.circle(screen, charge_color, (int(x), int(y)), 5)

class AdvancedCircuitCalculator:
    @staticmethod
    def solve_circuit(components, wires):
        AdvancedCircuitCalculator.reset_circuit(components)
        
        batteries = [comp for comp in components if isinstance(comp, Battery) and not comp.is_burned]
        if not batteries:
            return

        try:
            for battery in batteries:
                if battery.is_burned:
                    continue
                    
                connected_components = AdvancedCircuitCalculator.find_connected_components(battery)
                
                if len(connected_components) <= 1:
                    continue
                
                AdvancedCircuitCalculator.calculate_series_circuit(battery, connected_components, wires)
                
        except Exception as e:
            print(f"Ошибка расчета цепи: {e}")
            AdvancedCircuitCalculator.reset_circuit(components)

    @staticmethod
    def find_connected_components(start_component):
        visited = set()
        stack = [start_component]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in current.connected_to:
                if neighbor not in visited:
                    stack.append(neighbor)
        
        return list(visited)

    @staticmethod
    def calculate_series_circuit(battery, components, wires):
        total_resistance = battery.resistance
        
        for comp in components:
            if comp != battery and not comp.is_burned:
                if not isinstance(comp, Voltmeter):
                    total_resistance += comp.resistance
        
        if total_resistance <= 0:
            circuit_current = 0
        else:
            circuit_current = battery.voltage / total_resistance
        
        max_safe_current = 2.0
        if circuit_current > max_safe_current:
            circuit_current = max_safe_current
        
        battery.current = circuit_current
        
        for comp in components:
            if comp == battery:
                continue
                
            if not comp.is_burned:
                comp.current = circuit_current
                
                if not isinstance(comp, Voltmeter):
                    comp.voltage_drop = circuit_current * comp.resistance
                
                if isinstance(comp, Ammeter):
                    comp.measured_current = circuit_current
                
                comp.check_burn()
        
        AdvancedCircuitCalculator.calculate_voltmeters(components)
        
        for wire in wires:
            if wire.start_component in components and wire.end_component in components:
                wire.current = circuit_current

    @staticmethod
    def calculate_voltmeters(components):
        for comp in components:
            if isinstance(comp, Voltmeter) and not comp.is_burned:
                if len(comp.connected_to) >= 2:
                    comp1, comp2 = comp.connected_to[0], comp.connected_to[1]
                    voltage_diff = abs(comp1.voltage_drop - comp2.voltage_drop)
                    comp.measured_voltage = voltage_diff
                else:
                    comp.measured_voltage = 0

    @staticmethod
    def reset_circuit(components):
        for comp in components:
            comp.current = 0
            comp.voltage_drop = 0
            if isinstance(comp, Lamp):
                comp.is_lit = False
            if isinstance(comp, Ammeter):
                comp.measured_current = 0
            if isinstance(comp, Voltmeter):
                comp.measured_voltage = 0

class QuestSystem:
    def __init__(self):
        self.quests = [
            {
                "title": "Первая искра",
                "description": "Собери простую цепь с батареей и лампочкой",
                "condition": lambda sim: any(isinstance(comp, Lamp) and comp.is_lit for comp in sim.components),
                "reward": 100,
                "completed": False
            },
            {
                "title": "Ограничение тока",
                "description": "Добавь резистор в цепь",
                "condition": lambda sim: any(isinstance(comp, Resistor) and abs(comp.current) > 0 for comp in sim.components),
                "reward": 150,
                "completed": False
            },
            {
                "title": "Измерение тока",
                "description": "Используй амперметр для измерения тока",
                "condition": lambda sim: any(isinstance(comp, Ammeter) and abs(comp.measured_current) > 0 for comp in sim.components),
                "reward": 200,
                "completed": False
            },
            {
                "title": "Измерение напряжения", 
                "description": "Используй вольтметр для измерения напряжения",
                "condition": lambda sim: any(isinstance(comp, Voltmeter) and abs(comp.measured_voltage) > 0 for comp in sim.components),
                "reward": 200,
                "completed": False
            }
        ]
        self.current_quest = 0
        self.score = 0
        self.xp = 0
        self.level = 1
    
    def check_quests(self, simulator):
        quest_completed = False
        for i, quest in enumerate(self.quests):
            if not quest["completed"] and quest["condition"](simulator):
                quest["completed"] = True
                self.score += quest["reward"]
                self.xp += quest["reward"] // 10
                if self.xp >= self.level * 100:
                    self.level += 1
                    self.xp = 0
                quest_completed = True
                self.current_quest = min(i + 1, len(self.quests) - 1)
        
        return quest_completed
    
    def draw(self, screen):
        font_title = pygame.font.SysFont('arial', 20, bold=True)
        font_normal = pygame.font.SysFont('arial', 16)
        
        pygame.draw.rect(screen, UI_BG, (10, 10, 350, 120), border_radius=10)
        pygame.draw.rect(screen, UI_ACCENT, (10, 10, 350, 120), 2, border_radius=10)
        
        score_text = font_title.render(f"Очки: {self.score}", True, WHITE)
        level_text = font_normal.render(f"Уровень: {self.level}", True, UI_SECONDARY)
        xp_text = font_normal.render(f"Опыт: {self.xp}/{self.level * 100}", True, UI_WARNING)
        
        screen.blit(score_text, (20, 20))
        screen.blit(level_text, (20, 50))
        screen.blit(xp_text, (20, 75))
        
        if self.current_quest < len(self.quests):
            quest = self.quests[self.current_quest]
            status = "✓ ВЫПОЛНЕНО!" if quest["completed"] else "➤ В процессе..."
            status_color = GREEN if quest["completed"] else YELLOW
            
            pygame.draw.rect(screen, UI_BG, (10, 140, 350, 100), border_radius=10)
            pygame.draw.rect(screen, UI_ACCENT, (10, 140, 350, 100), 2, border_radius=10)
            
            quest_title = font_title.render(quest["title"], True, WHITE)
            quest_desc = pygame.font.SysFont('arial', 14).render(quest["description"], True, UI_WARNING)
            reward_text = font_normal.render(f"Награда: {quest['reward']} очков", True, GREEN)
            status_text = font_normal.render(status, True, status_color)
            
            screen.blit(quest_title, (20, 150))
            screen.blit(quest_desc, (20, 180))
            screen.blit(reward_text, (20, 205))
            screen.blit(status_text, (20, 230))

class CircuitSimulator:
    def __init__(self):
        self.components = []
        self.wires = []
        self.dragging_component = None
        self.dragging_offset_x = 0
        self.dragging_offset_y = 0
        self.selected_component = None
        self.connecting = False
        self.connection_start = None
        self.connection_start_point = None
        self.quest_system = QuestSystem()
        self.message = ""
        self.message_timer = 0
        self.toolbox_open = True
        self.calculator = AdvancedCircuitCalculator()
    
    def show_message(self, text, duration=3000):
        self.message = text
        self.message_timer = duration
    
    def add_component(self, component_type, x, y, **kwargs):
        if component_type == "resistor":
            new_comp = Resistor(x, y, **kwargs)
        elif component_type == "battery":
            new_comp = Battery(x, y, **kwargs)
        elif component_type == "lamp":
            new_comp = Lamp(x, y, **kwargs)
        elif component_type == "ammeter":
            new_comp = Ammeter(x, y, **kwargs)
        elif component_type == "voltmeter":
            new_comp = Voltmeter(x, y, **kwargs)
        else:
            return None
        self.components.append(new_comp)
        return new_comp
    
    def add_wire(self, start_comp, end_comp, start_point, end_point):
        if start_comp is None or end_comp is None:
            return None
        
        for wire in self.wires:
            if (wire.start_component == start_comp and wire.end_component == end_comp and
                wire.start_point == start_point and wire.end_point == end_point):
                return None
            if (wire.start_component == end_comp and wire.end_component == start_comp and
                wire.start_point == end_point and wire.end_point == start_point):
                return None
        
        try:
            new_wire = Wire(start_point, end_point, start_comp, end_comp)
            self.wires.append(new_wire)
            start_comp.connect(end_comp)
            return new_wire
        except Exception as e:
            print(f"Ошибка при создании провода: {e}")
            return None
    
    def solve_circuit(self):
        self.calculator.solve_circuit(self.components, self.wires)
        
        for wire in self.wires:
            if wire.start_component and wire.end_component:
                wire.current = wire.start_component.current
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if self.toolbox_open and 400 < mouse_x < 500 and 20 < mouse_y < 170:
                    if 20 < mouse_y < 50:
                        self.add_component("battery", 600, 300, voltage=9)
                    elif 50 < mouse_y < 80:
                        self.add_component("resistor", 600, 300, resistance=100)
                    elif 80 < mouse_y < 110:
                        self.add_component("lamp", 600, 300, resistance=50)
                    elif 110 < mouse_y < 140:
                        self.add_component("ammeter", 600, 300)
                    elif 140 < mouse_y < 170:
                        self.add_component("voltmeter", 600, 300)
                    continue
                
                if event.button == 1:
                    clicked_component = None
                    for comp in self.components:
                        distance = math.sqrt((comp.x - mouse_x)**2 + (comp.y - mouse_y)**2)
                        if distance < 50:
                            clicked_component = comp
                            break
                    
                    if clicked_component:
                        self.dragging_component = clicked_component
                        self.dragging_offset_x = clicked_component.x - mouse_x
                        self.dragging_offset_y = clicked_component.y - mouse_y
                        self.selected_component = clicked_component
                        clicked_component.is_selected = True
                        
                        for comp in self.components:
                            if comp != clicked_component:
                                comp.is_selected = False
                    else:
                        self.selected_component = None
                        for comp in self.components:
                            comp.is_selected = False
                
                elif event.button == 3:
                    connection_found = False
                    for comp in self.components:
                        points = comp.get_connection_points()
                        for point in points:
                            dist = math.sqrt((point[0] - mouse_x)**2 + (point[1] - mouse_y)**2)
                            if dist < 20:
                                if not self.connecting:
                                    self.connecting = True
                                    self.connection_start = comp
                                    self.connection_start_point = point
                                    connection_found = True
                                else:
                                    if comp != self.connection_start:
                                        if self.connection_start is not None and comp is not None:
                                            self.add_wire(self.connection_start, comp, 
                                                         self.connection_start_point, point)
                                            self.show_message("Соединение создано!", 1000)
                                    self.connecting = False
                                    self.connection_start = None
                                    self.connection_start_point = None
                                break
                        if connection_found:
                            break
                    
                    if not connection_found and self.connecting:
                        self.connecting = False
                        self.connection_start = None
                        self.connection_start_point = None
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_component = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_component:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.dragging_component.x = mouse_x + self.dragging_offset_x
                    self.dragging_component.y = mouse_y + self.dragging_offset_y
                    if hasattr(self.dragging_component, 'rect'):
                        self.dragging_component.rect.x = self.dragging_component.x - self.dragging_component.rect.width // 2
                        self.dragging_component.rect.y = self.dragging_component.y - self.dragging_component.rect.height // 2
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.add_component("resistor", 600, 300, resistance=100)
                elif event.key == pygame.K_b:
                    self.add_component("battery", 600, 300, voltage=9)
                elif event.key == pygame.K_l:
                    self.add_component("lamp", 600, 300, resistance=50)
                elif event.key == pygame.K_a:
                    self.add_component("ammeter", 600, 300)
                elif event.key == pygame.K_v:
                    self.add_component("voltmeter", 600, 300)
                elif event.key == pygame.K_c:
                    self.components.clear()
                    self.wires.clear()
                    self.show_message("Схема очищена", 1000)
                elif event.key == pygame.K_d and self.selected_component:
                    self.delete_component(self.selected_component)
                elif event.key == pygame.K_t:
                    self.toolbox_open = not self.toolbox_open
                elif event.key == pygame.K_SPACE:
                    if self.quest_system.check_quests(self):
                        self.show_message("Задание выполнено!", 2000)
    
    def delete_component(self, component):
        self.wires = [wire for wire in self.wires 
                     if wire.start_component != component and wire.end_component != component]
        
        for comp in self.components:
            comp.disconnect(component)
        
        if component in self.components:
            self.components.remove(component)
        
        self.selected_component = None
        self.show_message("Компонент удален", 1000)
    
    def draw_toolbox(self, screen):
        if not self.toolbox_open:
            return
        
        pygame.draw.rect(screen, UI_BG, (400, 20, 100, 170), border_radius=10)
        pygame.draw.rect(screen, UI_ACCENT, (400, 20, 100, 170), 2, border_radius=10)
        
        font = pygame.font.SysFont('arial', 12)
        
        buttons = [
            (410, 25, 80, 25, "Батарея (B)", WHITE),
            (410, 55, 80, 25, "Резистор (R)", WHITE),
            (410, 85, 80, 25, "Лампа (L)", WHITE),
            (410, 115, 80, 25, "Амперметр (A)", WHITE),
            (410, 145, 80, 25, "Вольтметр (V)", WHITE)
        ]
        
        for x, y, w, h, text, color in buttons:
            pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), border_radius=5)
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (x + 5, y + 6))
    
    def draw(self, screen):
        screen.fill(WHITE)
        
        for x in range(0, WIDTH, 25):
            pygame.draw.line(screen, (220, 220, 220), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 25):
            pygame.draw.line(screen, (220, 220, 220), (0, y), (WIDTH, y), 1)
        
        for wire in self.wires:
            wire.draw(screen)
        
        for component in self.components:
            component.draw(screen)
        
        if self.connecting and self.connection_start_point:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.draw.line(screen, GREEN, self.connection_start_point, (mouse_x, mouse_y), 3)
            pygame.draw.circle(screen, GREEN, self.connection_start_point, 6)
        
        self.draw_toolbox(screen)
        
        self.quest_system.draw(screen)
        
        if self.message_timer > 0:
            self.message_timer -= clock.get_time()
            font = pygame.font.SysFont('arial', 24, bold=True)
            text = font.render(self.message, True, YELLOW)
            text_rect = text.get_rect(center=(WIDTH//2, 50))
            
            pygame.draw.rect(screen, UI_BG, 
                           (text_rect.x-15, text_rect.y-10, text_rect.width+30, text_rect.height+20), 
                           border_radius=10)
            pygame.draw.rect(screen, UI_ACCENT, 
                           (text_rect.x-15, text_rect.y-10, text_rect.width+30, text_rect.height+20), 
                           2, border_radius=10)
            screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('arial', 16)
        instructions = [
            "ЛКМ: Перетаскивание | ПКМ: Соединение (клик по точкам)",
            "R/B/L/A/V: Добавить компонент | D: Удалить | C: Очистить",
            "T: Панель инструментов | SPACE: Проверить задание"
        ]
        for i, line in enumerate(instructions):
            text = font.render(line, True, UI_SECONDARY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 70 + i*20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            self.handle_events()
            self.solve_circuit()
            self.draw(screen)
            clock.tick(60)

if __name__ == "__main__":
    simulator = CircuitSimulator()
    simulator.run()