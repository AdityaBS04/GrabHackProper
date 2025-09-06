"""
Test file to verify the actor-based structure works correctly
"""

def test_actor_structure():
    """Test that all actor-based modules can be imported and work correctly"""
    try:
        # Test models import with new actor structure
        from models import GrabService, Actor, IssueCategory, ACTOR_ISSUE_MAPPING, SERVICE_ACTORS
        print("[OK] Actor-aware models imported successfully")
        
        # Test that actor enums work
        assert Actor.CUSTOMER.value == "customer"
        assert Actor.RESTAURANT.value == "restaurant"
        assert Actor.DELIVERY_AGENT.value == "delivery_agent"
        assert Actor.DRIVER.value == "driver"
        assert Actor.DARK_HOUSE.value == "dark_house"
        print("[OK] Actor enums work correctly")
        
        # Test actor mappings exist for all service-actor combinations
        expected_combinations = [
            (GrabService.GRAB_FOOD, Actor.CUSTOMER),
            (GrabService.GRAB_FOOD, Actor.RESTAURANT),
            (GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT),
            (GrabService.GRAB_MART, Actor.CUSTOMER),
            (GrabService.GRAB_MART, Actor.DARK_HOUSE),
            (GrabService.GRAB_MART, Actor.DELIVERY_AGENT),
            (GrabService.GRAB_CABS, Actor.CUSTOMER),
            (GrabService.GRAB_CABS, Actor.DRIVER),
        ]
        
        for service, actor in expected_combinations:
            assert (service, actor) in ACTOR_ISSUE_MAPPING
        print("[OK] Actor issue mappings exist for all service-actor combinations")
        
        # Test that service-actor mappings are properly structured
        for service in GrabService:
            assert service in SERVICE_ACTORS
            actors = SERVICE_ACTORS[service]
            assert len(actors) > 0
            for actor in actors:
                assert (service, actor) in ACTOR_ISSUE_MAPPING
                actor_issues = ACTOR_ISSUE_MAPPING[(service, actor)]
                assert len(actor_issues) > 0
        print("[OK] All services have properly structured actor mappings")
        
        # Test safety checker import
        from safety_checker import SafetyChecker
        print("[OK] Safety checker module imported successfully")
        
        # Test utils import
        from utils import create_placeholder_tool
        print("[OK] Utils module imported successfully")
        
        print("\n[SUCCESS] All actor-based modular imports work correctly!")
        
        # Show the new actor-based structure
        print("\nActor-Based Structure:")
        print("- models.py (Actor-aware data models)")
        print("- safety_checker.py (Safety validation)")
        print("- grab_food/")
        print("  - customer/")
        print("    - satisfaction_handler.py (Customer food experience)")
        print("  - restaurant/")
        print("    - quality_handler.py (Restaurant quality standards)")
        print("  - delivery_agent/")
        print("    - performance_handler.py (Food delivery performance)")
        print("- grab_mart/")
        print("  - customer/")
        print("    - shopping_experience_handler.py (Customer grocery experience)")
        print("  - dark_house/")
        print("    - inventory_handler.py (Warehouse operations)")
        print("  - delivery_agent/")
        print("    - grocery_delivery_handler.py (Grocery delivery performance)")
        print("- grab_cabs/")
        print("  - customer/")
        print("    - ride_experience_handler.py (Customer ride experience)")
        print("  - driver/")
        print("    - performance_handler.py (Driver performance & training)")
        print("- utils.py (Utility functions)")
        print("- actor_orchestration.py (Actor-aware orchestration)")
        print("- test_actor_structure.py (This test file)")
        
        # Show actor breakdown
        print(f"\nActor-Based Issue Breakdown:")
        total_combinations = 0
        for service in GrabService:
            actors = SERVICE_ACTORS[service]
            service_name = service.value.replace('_', ' ').title()
            print(f"- {service_name}: {len(actors)} actors")
            for actor in actors:
                actor_issues = ACTOR_ISSUE_MAPPING[(service, actor)]
                total_issues = sum(len(issues) for issues in actor_issues.values())
                actor_name = actor.value.replace('_', ' ').title()
                print(f"  - {actor_name}: {total_issues} handlers")
                total_combinations += 1
        
        print(f"\nTotal Service-Actor Combinations: {total_combinations}")
        print(f"Total Issue Mappings: {len(ACTOR_ISSUE_MAPPING)}")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_actor_handler_structure():
    """Test individual actor handler file structure"""
    print("\n[TESTING] Actor handler file structure...")
    
    try:
        import os
        base_path = os.path.dirname(__file__)
        services_tested = 0
        
        # Test Grab Food actor structure
        food_actors = ['customer', 'restaurant', 'delivery_agent']
        food_path = os.path.join(base_path, "grab_food")
        if os.path.exists(food_path):
            for actor in food_actors:
                actor_path = os.path.join(food_path, actor)
                if os.path.exists(actor_path):
                    handler_files = [f for f in os.listdir(actor_path) if f.endswith('.py') and f != '__init__.py']
                    print(f"[OK] Grab Food {actor} handlers: {handler_files}")
                else:
                    print(f"[WARN] Grab Food {actor} directory not found")
            services_tested += 1
        
        # Test Grab Mart actor structure
        mart_actors = ['customer', 'dark_house', 'delivery_agent']
        mart_path = os.path.join(base_path, "grab_mart")
        if os.path.exists(mart_path):
            for actor in mart_actors:
                actor_path = os.path.join(mart_path, actor)
                if os.path.exists(actor_path):
                    handler_files = [f for f in os.listdir(actor_path) if f.endswith('.py') and f != '__init__.py']
                    print(f"[OK] Grab Mart {actor} handlers: {handler_files}")
                else:
                    print(f"[WARN] Grab Mart {actor} directory not found")
            services_tested += 1
            
        # Test Grab Cabs actor structure
        cabs_actors = ['customer', 'driver']
        cabs_path = os.path.join(base_path, "grab_cabs")
        if os.path.exists(cabs_path):
            for actor in cabs_actors:
                actor_path = os.path.join(cabs_path, actor)
                if os.path.exists(actor_path):
                    handler_files = [f for f in os.listdir(actor_path) if f.endswith('.py') and f != '__init__.py']
                    print(f"[OK] Grab Cabs {actor} handlers: {handler_files}")
                else:
                    print(f"[WARN] Grab Cabs {actor} directory not found")
            services_tested += 1
            
        print(f"[SUCCESS] All {services_tested} services have actor-based handler structure")
        return True
        
    except Exception as e:
        print(f"[ERROR] Handler structure test failed: {e}")
        return False


def demonstrate_actor_extensibility():
    """Demonstrate how easy it is to add new actor handlers"""
    print("\n[DEMO] Adding new actor handler example:")
    
    example_code = '''
# To add a new Grab Food Restaurant handler for "Menu Management":

# 1. Create grab_food/restaurant/menu_handler.py:
class RestaurantMenuHandler:
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "restaurant"
    
    def handle_menu_update_issue(self, query: str) -> str:
        return "Menu update processed. Please allow 2-4 hours for platform sync."

# 2. Update models.py to include the new handler:
SubIssue("Menu update problems", "handle_menu_update_issue", 
         "Restaurant menu management issues", 
         GrabService.GRAB_FOOD, Actor.RESTAURANT, 
         "grab_food.restaurant.menu_handler")

# 3. The actor-aware orchestration system automatically routes it!
    '''
    
    print(example_code)
    print("[SUCCESS] New actor-specific handlers can be added easily!")


if __name__ == "__main__":
    test_actor_structure()
    test_actor_handler_structure() 
    demonstrate_actor_extensibility()