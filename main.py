# main.py

import pygame
import sys
import random
import time
from datetime import datetime
import redis

# Initialize Pygame
pygame.init()

# Game Settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (128, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Texas Transit Tycoon")

# Load Images (Placeholders for actual images)
# Replace 'path/to/image.png' with actual image paths
title_image = pygame.Surface((400, 100))  # Placeholder surface
title_image.fill((0, 128, 255))  # Temporary color
title_font = pygame.font.SysFont(None, 72)
title_text = title_font.render("Texas Transit Tycoon", True, WHITE)
title_image.blit(title_text, (50, 25))

# Define Fonts
font = pygame.font.SysFont(None, 24)

# Define Clock
clock = pygame.time.Clock()

# ---------------------
# Data Model Classes
# ---------------------

class Road:
    def __init__(self, road_id, name, start_point, end_point, length, lanes, condition_rating, traffic_volume, capacity):
        self.road_id = road_id
        self.name = name
        self.start_point = start_point  # (x, y) coordinates
        self.end_point = end_point
        self.length = length  # In miles
        self.lanes = lanes  # Number of lanes
        self.condition_rating = condition_rating  # 0 (worst) to 100 (best)
        self.traffic_volume = traffic_volume  # Vehicles per day
        self.capacity = capacity  # Max vehicles per day

    def degrade_condition(self, degradation_rate):
        """Simulate condition degradation based on traffic and other factors."""
        usage_factor = self.traffic_volume / self.capacity
        environmental_factor = random.uniform(0.1, 0.3)  # Placeholder for environmental impact
        total_degradation = degradation_rate * (1 + usage_factor + environmental_factor)
        self.condition_rating -= total_degradation
        self.condition_rating = max(self.condition_rating, 0)  # Prevent negative condition
        print(f"Road {self.name} condition degraded by {total_degradation:.2f}. New condition: {self.condition_rating:.2f}")

    def repair(self, repair_amount):
        """Repair the road to improve condition."""
        self.condition_rating += repair_amount
        self.condition_rating = min(self.condition_rating, 100)  # Cap condition at 100
        print(f"Road {self.name} repaired by {repair_amount}. New condition: {self.condition_rating:.2f}")

class Project:
    def __init__(self, project_id, name, project_type, assets, estimated_cost, allocated_budget, start_date, end_date, status):
        self.project_id = project_id
        self.name = name
        self.project_type = project_type  # 'Construction', 'Maintenance', 'Upgrade'
        self.assets = assets  # List of Road instances
        self.estimated_cost = estimated_cost
        self.allocated_budget = allocated_budget
        self.start_date = start_date  # Integer representing day count
        self.end_date = end_date  # Integer representing day count
        self.status = status  # 'Proposed', 'Approved', 'In Progress', 'Completed', 'Cancelled'
        self.current_progress = 0  # Percentage (0-100)
        self.assigned_contractor = None
        self.bid_amount = 0
        self.completion_time = 0  # In days

    def update_progress(self, days_elapsed):
        if self.status == 'In Progress':
            total_days = self.end_date - self.start_date
            if total_days <= 0:
                progress_increment = 100 - self.current_progress
            else:
                progress_increment = (days_elapsed / total_days) * 100
            self.current_progress += progress_increment
            if self.current_progress >= 100:
                self.current_progress = 100
                self.status = 'Completed'
                self.complete_project()
            print(f"Project {self.name} progress updated to {self.current_progress:.2f}%.")

    def complete_project(self):
        print(f"Project {self.name} has been completed.")
        # Implement any post-completion logic here, e.g., updating asset conditions

    def cancel_project(self):
        self.status = 'Cancelled'
        print(f"Project {self.name} has been cancelled.")

class Budget:
    def __init__(self, fiscal_year, total_budget):
        self.fiscal_year = fiscal_year
        self.total_budget = total_budget
        self.allocated_funds = 0
        self.available_funds = total_budget

    def allocate_funds(self, amount):
        if amount > self.available_funds:
            print("Insufficient funds to allocate.")
            return False
        self.allocated_funds += amount
        self.available_funds -= amount
        print(f"Allocated ${amount} to projects. Available funds: ${self.available_funds}.")
        return True

    def deallocate_funds(self, amount):
        self.allocated_funds -= amount
        self.available_funds += amount
        print(f"Deallocated ${amount} from projects. Available funds: ${self.available_funds}.")

class Contractor:
    def __init__(self, contractor_id, name, expertise, rating, bid_history=None):
        self.contractor_id = contractor_id
        self.name = name
        self.expertise = expertise  # List of specialties
        self.rating = rating  # 0 to 5 stars
        self.bid_history = bid_history if bid_history else []  # List of past bids

    def submit_bid(self, project, bid_amount, completion_time):
        bid = {
            'project_id': project.project_id,
            'bid_amount': bid_amount,
            'completion_time': completion_time  # In days
        }
        self.bid_history.append(bid)
        print(f"Contractor {self.name} submitted a bid of ${bid_amount:.2f} with completion time {completion_time} days for project {project.name}.")
        return bid

class Event:
    def __init__(self, event_id, name, event_type, affected_assets, impact_level, date):
        self.event_id = event_id
        self.name = name
        self.event_type = event_type  # 'Natural Disaster', 'Economic Shift', 'Political Change'
        self.affected_assets = affected_assets  # List of Road instances
        self.impact_level = impact_level  # 'Minor', 'Moderate', 'Severe'
        self.date = date  # Integer representing day count

    def apply_event(self):
        """Apply the event's impact to affected assets."""
        print(f"Applying event '{self.name}' affecting {len(self.affected_assets)} assets.")
        for asset in self.affected_assets:
            if self.event_type == 'Natural Disaster':
                damage = {'Minor': 5, 'Moderate': 15, 'Severe': 30}[self.impact_level]
                asset.condition_rating -= damage
                asset.condition_rating = max(asset.condition_rating, 0)
                print(f"Asset {asset.name} damaged by {damage}. New condition: {asset.condition_rating}")
            elif self.event_type == 'Economic Shift':
                # Implement economic impact logic
                pass
            elif self.event_type == 'Political Change':
                # Implement political impact logic
                pass

# RSX API Client Placeholder
class RSXClient:
    def __init__(self):
        # Initialize connection parameters
        pass

    def authenticate(self):
        # Authenticate with RSX API
        pass

    def send_request(self, endpoint, data):
        # Send a request to the RSX API
        pass

    def get_robot_status(self, robot_id):
        # Retrieve status of a specific robot
        pass

# ---------------------
# Game Engine Class
# ---------------------

class GameEngine:
    def __init__(self):
        # Initialize Redis client
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            # Test connection
            self.redis_client.ping()
            print("Connected to Redis successfully.")
        except redis.ConnectionError:
            print("Failed to connect to Redis. Make sure Redis server is running.")
            self.redis_client = None

        # Initialize RSX API client
        self.rsx_client = RSXClient()

        # Initialize budget
        self.budget = Budget(fiscal_year=2024, total_budget=1000000)  # Starting with $1,000,000

        # Initialize projects
        self.projects = []

        # Initialize contractors
        self.contractors = self.initialize_contractors()

        # Initialize infrastructure assets
        self.infrastructure_assets = self.initialize_infrastructure()

        # Initialize events
        self.events = []

        # Initialize game state variables
        self.is_running = True
        self.current_day = 0  # Start at day 0
        self.last_update_time = time.time()

        # Initialize game state
        self.current_state = STATE_MAIN_MENU  # Encapsulated within GameEngine

    def initialize_contractors(self):
        # Initialize a list of contractors
        contractors = [
            Contractor(contractor_id=1, name="TexBuild Co.", expertise=["Road", "Bridge"], rating=4.5),
            Contractor(contractor_id=2, name="LoneStar Construction", expertise=["Tunnel", "Road"], rating=4.0),
            Contractor(contractor_id=3, name="RoadMasters", expertise=["Road"], rating=3.8),
        ]
        return contractors

    def initialize_infrastructure(self):
        # Initialize a list of infrastructure assets
        roads = [
            Road(road_id=1, name="I-35", start_point=(100, 100), end_point=(700, 100), length=300, lanes=4, condition_rating=80, traffic_volume=20000, capacity=25000),
            Road(road_id=2, name="US-290", start_point=(100, 200), end_point=(700, 200), length=250, lanes=3, condition_rating=70, traffic_volume=15000, capacity=20000),
            Road(road_id=3, name="Loop 1604", start_point=(100, 300), end_point=(700, 300), length=150, lanes=2, condition_rating=60, traffic_volume=10000, capacity=15000),
            # Add more roads as needed
        ]
        return roads

    def propose_project(self, name, project_type, assets, estimated_cost, start_day, duration_days):
        """Propose a new project."""
        project_id = len(self.projects) + 1
        start_date = self.current_day + start_day
        end_date = start_date + duration_days
        project = Project(
            project_id=project_id,
            name=name,
            project_type=project_type,
            assets=assets,
            estimated_cost=estimated_cost,
            allocated_budget=0,
            start_date=start_date,
            end_date=end_date,
            status='Proposed'
        )
        self.projects.append(project)
        print(f"Proposed new project: {project.name} (ID: {project.project_id})")
        return project

    def approve_project(self, project):
        """Approve a proposed project and allocate budget."""
        if project.status != 'Proposed':
            print(f"Project {project.name} is not in a proposed state.")
            return False
        if self.budget.allocate_funds(project.estimated_cost):
            project.allocated_budget = project.estimated_cost
            project.status = 'Approved'
            print(f"Project {project.name} has been approved and allocated ${project.allocated_budget}.")
            return True
        else:
            print(f"Insufficient funds to approve project {project.name}.")
            return False

    def assign_contractor_to_project(self, project):
        """Assign a contractor to an approved project based on bids."""
        print(f"Assigning contractor to project {project.name}...")
        # Simulate bidding process
        bids = []
        for contractor in self.contractors:
            bid_amount = project.estimated_cost * random.uniform(0.9, 1.1)  # ±10% variation
            completion_time = random.randint(30, 90)  # Completion time in days
            bid = contractor.submit_bid(project, bid_amount, completion_time)
            bids.append((contractor, bid))
        
        # Select the best bid based on lowest amount and highest contractor rating
        bids_sorted = sorted(bids, key=lambda x: (x[1]['bid_amount'], -x[0].rating))
        selected_contractor, selected_bid = bids_sorted[0]
        project.assigned_contractor = selected_contractor
        project.bid_amount = selected_bid['bid_amount']
        project.completion_time = selected_bid['completion_time']
        project.status = 'In Progress'
        print(f"Contractor {selected_contractor.name} has been assigned to project {project.name} with bid ${selected_bid['bid_amount']:.2f} and completion time {selected_bid['completion_time']} days.")

    def propose_new_project(self):
        """Allow the player to propose a new project."""
        # For simplicity, we'll simulate a project proposal
        name = f"Upgrade {random.choice(['I-35', 'US-290', 'Loop 1604'])}"
        project_type = random.choice(['Construction', 'Maintenance', 'Upgrade'])
        asset = random.choice(self.infrastructure_assets)
        estimated_cost = random.randint(50000, 200000)  # Random cost between $50k and $200k
        start_day = random.randint(1, 10)  # Start within next 10 days
        duration_days = random.randint(30, 90)  # Duration between 1 to 3 months
        project = self.propose_project(name, project_type, [asset], estimated_cost, start_day, duration_days)
        return project

    def update_projects(self):
        """Update the progress of all projects."""
        for project in self.projects:
            if project.status == 'In Progress':
                days_elapsed = 1  # Assuming one day per game day
                project.update_progress(days_elapsed)
                if project.status == 'Completed':
                    self.budget.deallocate_funds(project.allocated_budget)  # Release allocated funds
                    # Implement any post-completion effects on assets
                    for asset in project.assets:
                        if project.project_type in ['Maintenance', 'Upgrade']:
                            repair_amount = random.randint(10, 30)  # Repair by 10-30 points
                            asset.repair(repair_amount)
                    self.notify_player(f"Project {project.name} has been completed.")

    def degrade_infrastructure(self):
        """Simulate infrastructure condition degradation."""
        for asset in self.infrastructure_assets:
            degradation_rate = 0.1  # Base degradation rate per day
            asset.degrade_condition(degradation_rate)

    def perform_maintenance(self, asset, repair_amount):
        """Allow the player to perform maintenance on an asset."""
        cost = repair_amount * 1000  # Assume $1,000 per repair unit
        if self.budget.allocate_funds(cost):
            asset.repair(repair_amount)
            print(f"Performed maintenance on {asset.name} for ${cost}.")
            self.notify_player(f"Performed maintenance on {asset.name} for ${cost}.")
            return True
        else:
            print(f"Insufficient funds to perform maintenance on {asset.name}.")
            self.notify_player(f"Insufficient funds to perform maintenance on {asset.name}.")
            return False

    def generate_random_event(self):
        """Randomly generate an event based on probability."""
        event_chance = random.random()
        if event_chance < 0.05:  # 5% chance each day
            event_type = random.choice(['Natural Disaster', 'Economic Shift', 'Political Change'])
            if event_type == 'Natural Disaster':
                name = "Heavy Rainstorm"
                impact_level = random.choice(['Minor', 'Moderate', 'Severe'])
                affected_assets = random.sample(self.infrastructure_assets, k=random.randint(1, 3))
                event = Event(event_id=len(self.events)+1, name=name, event_type=event_type, affected_assets=affected_assets, impact_level=impact_level, date=self.current_day)
                event.apply_event()
                self.events.append(event)
                self.notify_player(f"Event '{name}' occurred affecting {len(affected_assets)} assets.")
            # Implement other event types as needed

    def handle_events(self):
        """Handle events scheduled for the current day."""
        for event in self.events:
            if event.date == self.current_day:
                event.apply_event()
                self.notify_player(f"Event '{event.name}' is happening today.")

    def notify_player(self, message):
        """Display a notification message to the player."""
        # For simplicity, print to console. Later, integrate with Pygame UI.
        print(f"Notification: {message}")

    def run_day_cycle(self):
        """Simulate a single day in the game."""
        self.current_day += 1
        print(f"\n--- Day {self.current_day} ---")
        
        # Degrade infrastructure
        self.degrade_infrastructure()
        
        # Update projects
        self.update_projects()
        
        # Handle events
        self.generate_random_event()
        self.handle_events()
        
        # Generate new project proposals periodically
        if self.current_day % 30 == 0:  # Every 30 days
            self.propose_new_project()

    def run(self):
        while self.is_running:
            current_time = time.time()
            elapsed_time = current_time - self.last_update_time
            if elapsed_time >= 1:  # Progress one day every second
                self.run_day_cycle()
                self.last_update_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.current_state == STATE_MAIN_MENU:
                    self.handle_main_menu_events(event)
                elif self.current_state == STATE_GAMEPLAY:
                    self.handle_gameplay_events(event)
                elif self.current_state == STATE_PAUSE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.current_state = STATE_GAMEPLAY

            # Render
            if self.current_state == STATE_MAIN_MENU:
                self.draw_main_menu()
            elif self.current_state == STATE_GAMEPLAY:
                self.draw_gameplay()
            elif self.current_state == STATE_PAUSE:
                self.draw_gameplay()
                self.draw_pause_menu()

            pygame.display.flip()
            clock.tick(FPS)

    def initialize_game(self):
        """Set up initial game state."""
        print("Initializing game...")
        self.rsx_client.authenticate()
        # Load initial data into Redis if needed
        # Example:
        # self.redis_client.set('key', 'value')

    def draw_gameplay_info(self):
        """Display current day and budget on the gameplay screen."""
        day_text = font.render(f"Day: {self.current_day}", True, BLACK)
        budget_text = font.render(f"Budget: ${self.budget.available_funds}", True, BLACK)
        screen.blit(day_text, (50, 50))
        screen.blit(budget_text, (50, 100))
        
        # Display list of projects
        y_offset = 150
        project_title = font.render("Projects:", True, BLACK)
        screen.blit(project_title, (50, y_offset))
        y_offset += 30
        for project in self.projects:
            contractor_name = project.assigned_contractor.name if project.assigned_contractor else "Unassigned"
            project_status = f"{project.name} - {project.status} - Progress: {project.current_progress:.1f}% - Contractor: {contractor_name}"
            project_text = font.render(project_status, True, BLACK)
            screen.blit(project_text, (50, y_offset))
            y_offset += 30

    def handle_main_menu_events(self, event):
        """Handle events in the main menu."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 50)
            if start_button_rect.collidepoint(mouse_pos):
                self.current_state = STATE_GAMEPLAY

    def handle_gameplay_events(self, event):
        """Handle events in the gameplay screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.current_state = STATE_PAUSE
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if Propose Project button is clicked
            if 50 <= mouse_pos[0] <= 250 and 500 <= mouse_pos[1] <= 550:
                project = self.propose_new_project()
                approved = self.approve_project(project)
                if approved:
                    self.assign_contractor_to_project(project)
            # Check if Perform Maintenance button is clicked
            elif 300 <= mouse_pos[0] <= 500 and 500 <= mouse_pos[1] <= 550:
                # For simplicity, perform maintenance on a random asset
                if self.infrastructure_assets:
                    asset = random.choice(self.infrastructure_assets)
                    repair_amount = random.randint(5, 20)  # Repair between 5 and 20 condition points
                    self.perform_maintenance(asset, repair_amount)

    def draw_main_menu(self):
        """Draw the main menu screen."""
        screen.fill(WHITE)
        # Draw Title Image
        screen.blit(title_image, (SCREEN_WIDTH//2 - title_image.get_width()//2, 100))
        
        # Draw Start Button
        start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button_rect)
        start_text = font.render("Start Game", True, WHITE)
        screen.blit(start_text, (start_button_rect.x + 50, start_button_rect.y + 15))

    def draw_gameplay(self):
        """Draw the gameplay screen."""
        screen.fill(WHITE)
        # Display gameplay information
        self.draw_gameplay_info()
        
        # Display infrastructure assets
        x_start = 400
        y_start = 50
        asset_title = font.render("Infrastructure Assets:", True, BLACK)
        screen.blit(asset_title, (x_start, y_start))
        y_start += 30
        for asset in self.infrastructure_assets:
            asset_text = font.render(f"{asset.name}: Condition {asset.condition_rating:.1f}", True, BLACK)
            screen.blit(asset_text, (x_start, y_start))
            y_start += 30
        
        # Display buttons
        propose_button_rect = pygame.Rect(50, 500, 200, 50)
        pygame.draw.rect(screen, GREEN, propose_button_rect)
        propose_text = font.render("Propose Project", True, WHITE)
        screen.blit(propose_text, (propose_button_rect.x + 10, propose_button_rect.y + 10))
        
        maintenance_button_rect = pygame.Rect(300, 500, 200, 50)
        pygame.draw.rect(screen, RED, maintenance_button_rect)
        maintenance_text = font.render("Perform Maintenance", True, WHITE)
        screen.blit(maintenance_text, (maintenance_button_rect.x + 10, maintenance_button_rect.y + 10))

    def draw_pause_menu(self):
        """Draw the pause menu overlay."""
        # Semi-transparent overlay
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 128))  # Black with 50% opacity
        screen.blit(pause_overlay, (0, 0))
        
        pause_text = font.render("Paused - Press P to Resume", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))

# ---------------------
# Game States
# ---------------------

STATE_MAIN_MENU = 'main_menu'
STATE_GAMEPLAY = 'gameplay'
STATE_PAUSE = 'pause'
STATE_GAME_OVER = 'game_over'

# ---------------------
# Main Function
# ---------------------

def main():
    game_engine = GameEngine()
    game_engine.run()

if __name__ == "__main__":
    main()
