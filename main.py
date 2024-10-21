import json

class GameEngine:
    # Existing methods...

    def save_game_state(self):
        """Serialize and save the game state to Redis."""
        game_state = {
            'current_day': self.current_day,
            'budget': {
                'fiscal_year': self.budget.fiscal_year,
                'total_budget': self.budget.total_budget,
                'allocated_funds': self.budget.allocated_funds,
                'available_funds': self.budget.available_funds
            },
            'projects': [
                {
                    'project_id': p.project_id,
                    'name': p.name,
                    'project_type': p.project_type,
                    'assets': [a.name for a in p.assets],
                    'estimated_cost': p.estimated_cost,
                    'allocated_budget': p.allocated_budget,
                    'start_date': p.start_date,
                    'end_date': p.end_date,
                    'status': p.status,
                    'current_progress': p.current_progress,
                    'assigned_contractor': p.assigned_contractor.name if p.assigned_contractor else None,
                    'bid_amount': p.bid_amount,
                    'completion_time': p.completion_time
                }
                for p in self.projects
            ],
            'infrastructure_assets': [
                {
                    'road_id': a.road_id,
                    'name': a.name,
                    'start_point': a.start_point,
                    'end_point': a.end_point,
                    'length': a.length,
                    'lanes': a.lanes,
                    'condition_rating': a.condition_rating,
                    'traffic_volume': a.traffic_volume,
                    'capacity': a.capacity
                }
                for a in self.infrastructure_assets
            ]
            # Add more components as needed
        }
        serialized_state = json.dumps(game_state)
        if self.redis_client:
            self.redis_client.set('game_state', serialized_state)
            print("Game state saved successfully.")
        else:
            print("Redis client not available. Cannot save game state.")

    def load_game_state(self):
        """Load and deserialize the game state from Redis."""
        if self.redis_client:
            serialized_state = self.redis_client.get('game_state')
            if serialized_state:
                game_state = json.loads(serialized_state)
                self.current_day = game_state['current_day']
                self.budget.fiscal_year = game_state['budget']['fiscal_year']
                self.budget.total_budget = game_state['budget']['total_budget']
                self.budget.allocated_funds = game_state['budget']['allocated_funds']
                self.budget.available_funds = game_state['budget']['available_funds']
                # Load projects
                self.projects = []
                for p in game_state['projects']:
                    assets = [a for a in self.infrastructure_assets if a.name in p['assets']]
                    project = Project(
                        project_id=p['project_id'],
                        name=p['name'],
                        project_type=p['project_type'],
                        assets=assets,
                        estimated_cost=p['estimated_cost'],
                        allocated_budget=p['allocated_budget'],
                        start_date=p['start_date'],
                        end_date=p['end_date'],
                        status=p['status']
                    )
                    project.current_progress = p['current_progress']
                    if p['assigned_contractor']:
                        contractor = next((c for c in self.contractors if c.name == p['assigned_contractor']), None)
                        project.assigned_contractor = contractor
                    project.bid_amount = p['bid_amount']
                    project.completion_time = p['completion_time']
                    self.projects.append(project)
                # Load infrastructure assets
                for a in game_state['infrastructure_assets']:
                    asset = next((road for road in self.infrastructure_assets if road.name == a['name']), None)
                    if asset:
                        asset.condition_rating = a['condition_rating']
                        asset.traffic_volume = a['traffic_volume']
                        asset.capacity = a['capacity']
                print("Game state loaded successfully.")
            else:
                print("No saved game state found.")
        else:
            print("Redis client not available. Cannot load game state.")
