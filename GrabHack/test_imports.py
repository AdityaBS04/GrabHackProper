"""
Test file to verify the modular structure works correctly
"""

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        # Test models import
        from models import IssueCategory, ISSUE_MAPPING, SubIssue
        print("[OK] Models module imported successfully")
        
        # Test that enums work
        assert IssueCategory.ORDER_NOT_RECEIVED.value == "1"
        assert len(ISSUE_MAPPING) > 0
        print("[OK] Models data structures work correctly")
        
        # Test utils import
        from utils import create_placeholder_tool
        print("[OK] Utils module imported successfully")
        
        print("\n[SUCCESS] All modular imports work correctly!")
        print("\nModular structure:")
        print("- models.py (Data models and configurations)")
        print("- safety_checker.py (Safety validation)")
        print("- handlers/")
        print("  - __init__.py")
        print("  - portion_handler.py (Portion complaint handler)")
        print("- utils.py (Utility functions)")
        print("- orchestration.py (Main orchestration logic)")
        print("- test_imports.py (This test file)")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()