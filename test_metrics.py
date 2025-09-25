#!/usr/bin/env python3
"""
Simple test script to verify metrics collection is working.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_metrics_import():
    """Test that metrics can be imported and basic functionality works."""
    print("Testing metrics import...")
    
    try:
        from base.metrics import metrics, PrometheusMetrics
        print("✅ Successfully imported metrics")
    except ImportError as e:
        print(f"❌ Failed to import metrics: {e}")
        return False
    
    return True

def test_metrics_basic_functionality():
    """Test basic metrics functionality."""
    print("\nTesting basic metrics functionality...")
    
    try:
        from base.metrics import metrics
        
        # Test recording various metrics
        metrics.record_http_request("GET", "/test", 200, 0.1)
        print("✅ HTTP request metric recorded")
        
        metrics.record_auth_attempt("success")
        print("✅ Auth attempt metric recorded")
        
        metrics.record_k8s_request("pod", "list", "default", "success", 0.05)
        print("✅ K8s request metric recorded")
        
        metrics.update_resource_count("pod", "default", 5)
        print("✅ Resource count metric updated")
        
        # Test metrics generation
        metrics_output = metrics.generate_metrics()
        if "http_requests_total" in metrics_output:
            print("✅ Metrics generation working")
        else:
            print("❌ Metrics generation not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing metrics functionality: {e}")
        return False
    
    return True

def test_middleware_import():
    """Test that middleware can be imported."""
    print("\nTesting middleware import...")
    
    try:
        from base.middleware import PrometheusMiddleware
        print("✅ Successfully imported PrometheusMiddleware")
    except ImportError as e:
        print(f"❌ Failed to import PrometheusMiddleware: {e}")
        return False
    
    return True

def test_metrics_router_import():
    """Test that metrics router can be imported."""
    print("\nTesting metrics router import...")
    
    try:
        from base.metrics_router import router
        print("✅ Successfully imported metrics router")
    except ImportError as e:
        print(f"❌ Failed to import metrics router: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting K8s Resource Explorer Metrics Tests\n")
    
    tests = [
        test_metrics_import,
        test_metrics_basic_functionality,
        test_middleware_import,
        test_metrics_router_import,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Metrics system is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())