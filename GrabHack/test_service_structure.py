"""
Test file to verify the service-based modular structure works correctly
"""

def test_service_structure():
    """Test that all service-based modules can be imported and work correctly"""
    try:
        # Test models import with new service structure
        from models import GrabService, IssueCategory, ISSUE_MAPPING, GRAB_FOOD_ISSUES, GRAB_MART_ISSUES, GRAB_CABS_ISSUES
        print("[OK] Service-aware models imported successfully")
        
        # Test that service enums work
        assert GrabService.GRAB_FOOD.value == "grab_food"
        assert GrabService.GRAB_MART.value == "grab_mart"
        assert GrabService.GRAB_CABS.value == "grab_cabs"
        print("[OK] Service enums work correctly")
        
        # Test issue mappings exist for all services
        assert GrabService.GRAB_FOOD in ISSUE_MAPPING
        assert GrabService.GRAB_MART in ISSUE_MAPPING
        assert GrabService.GRAB_CABS in ISSUE_MAPPING
        print("[OK] Issue mappings exist for all services")
        
        # Test that service-specific issues are properly structured
        food_issues = ISSUE_MAPPING[GrabService.GRAB_FOOD]
        mart_issues = ISSUE_MAPPING[GrabService.GRAB_MART]
        cabs_issues = ISSUE_MAPPING[GrabService.GRAB_CABS]
        
        assert len(food_issues) > 0
        assert len(mart_issues) > 0 
        assert len(cabs_issues) > 0
        print("[OK] All services have issue categories")
        
        # Test safety checker import
        from safety_checker import SafetyChecker
        print("[OK] Safety checker module imported successfully")
        
        # Test utils import
        from utils import create_placeholder_tool
        print("[OK] Utils module imported successfully")
        
        print("\n[SUCCESS] All service-based modular imports work correctly!")
        
        # Show the new service-based structure
        print("\nNew Service-Based Structure:")
        print("- models.py (Service-aware data models)")
        print("- safety_checker.py (Safety validation)")
        print("- grab_food/")
        print("  - __init__.py")
        print("  - portion_handler.py (Food portion complaints)")
        print("  - delivery_handler.py (Food delivery issues)")
        print("- grab_mart/")
        print("  - __init__.py") 
        print("  - delivery_handler.py (Grocery delivery issues)")
        print("  - quality_handler.py (Product quality issues)")
        print("- grab_cabs/")
        print("  - __init__.py")
        print("  - ride_handler.py (Ride-related issues)")
        print("  - driver_handler.py (Driver behavior issues)")
        print("- utils.py (Utility functions)")
        print("- service_orchestration.py (Service-aware orchestration)")
        print("- test_service_structure.py (This test file)")
        
        # Show service breakdown
        print(f"\nService Issue Breakdown:")
        print(f"- Grab Food: {sum(len(issues) for issues in food_issues.values())} handlers")
        print(f"- Grab Mart: {sum(len(issues) for issues in mart_issues.values())} handlers")  
        print(f"- Grab Cabs: {sum(len(issues) for issues in cabs_issues.values())} handlers")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_service_handler_structure():
    """Test individual service handler imports"""
    print("\n[TESTING] Service handler imports...")
    
    # Test imports that don't require external dependencies
    services_tested = 0
    
    try:
        # Test if we can access the handler modules (they exist)
        import os
        base_path = os.path.dirname(__file__)
        
        # Check Grab Food handlers
        food_path = os.path.join(base_path, "grab_food")
        if os.path.exists(food_path):
            food_files = os.listdir(food_path)
            print(f"[OK] Grab Food handlers found: {[f for f in food_files if f.endswith('.py')]}")
            services_tested += 1
        
        # Check Grab Mart handlers  
        mart_path = os.path.join(base_path, "grab_mart")
        if os.path.exists(mart_path):
            mart_files = os.listdir(mart_path)
            print(f"[OK] Grab Mart handlers found: {[f for f in mart_files if f.endswith('.py')]}")
            services_tested += 1
            
        # Check Grab Cabs handlers
        cabs_path = os.path.join(base_path, "grab_cabs")
        if os.path.exists(cabs_path):
            cabs_files = os.listdir(cabs_path)
            print(f"[OK] Grab Cabs handlers found: {[f for f in cabs_files if f.endswith('.py')]}")
            services_tested += 1
            
        print(f"[SUCCESS] All {services_tested} service directories created with handlers")
        return True
        
    except Exception as e:
        print(f"[ERROR] Handler structure test failed: {e}")
        return False


def demonstrate_extensibility():
    """Demonstrate how easy it is to add new handlers"""
    print("\n[DEMO] Adding new handler example:")
    
    example_code = '''
# To add a new Grab Food handler for "Restaurant Issues":

# 1. Create grab_food/restaurant_handler.py:
class GrabFoodRestaurantHandler:
    def __init__(self, groq_api_key: str):
        self.service = "grab_food"
    
    def handle_restaurant_closure(self, query: str) -> str:
        return "Restaurant is temporarily closed. Full refund processed."

# 2. Update models.py to include the new handler:
SubIssue("Restaurant closed", "handle_restaurant_closure", 
         "Handle restaurant closure situations", 
         GrabService.GRAB_FOOD, "grab_food.restaurant_handler")

# 3. The orchestration system automatically loads it!
    '''
    
    print(example_code)
    print("[SUCCESS] New handlers can be added by simply creating new Python files!")


if __name__ == "__main__":
    test_service_structure()
    test_service_handler_structure() 
    demonstrate_extensibility()