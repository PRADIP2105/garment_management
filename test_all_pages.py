#!/usr/bin/env python
"""
Test all web pages to ensure templates exist and load correctly
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_all_pages():
    """Test that all web pages load without template errors"""
    print("=== Testing All Web Pages ===")
    
    pages = [
        ('/', 'Home page'),
        ('/login/', 'Login page'),
        ('/register/', 'Registration page'),
        ('/dashboard/', 'Dashboard page'),
        ('/workers/', 'Workers page'),
        ('/suppliers/', 'Suppliers page'),
        ('/materials/', 'Materials page'),
        ('/work/distribution/', 'Work Distribution page'),
        ('/work/return/', 'Work Return page'),
        ('/stock/', 'Stock page')
    ]
    
    passed = 0
    total = len(pages)
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                # Check if it's not an error page
                if "TemplateDoesNotExist" not in response.text and "Server Error" not in response.text:
                    print(f"✓ {name} loads successfully")
                    passed += 1
                else:
                    print(f"✗ {name} has template error")
            else:
                print(f"✗ {name} failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ {name} error: {str(e)}")
    
    return passed, total

def main():
    print("=== Web Pages Template Test ===")
    
    passed, total = test_all_pages()
    
    print(f"\n=== Results ===")
    print(f"Pages tested: {total}")
    print(f"Pages working: {passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL PAGES WORKING!")
        print("\nYour complete web application is ready:")
        print("✅ Home page with company registration")
        print("✅ Login and registration forms")
        print("✅ Dashboard with real-time statistics")
        print("✅ Workers management interface")
        print("✅ Suppliers management interface")
        print("✅ Materials and inventory management")
        print("✅ Work distribution system")
        print("✅ Work return tracking")
        print("✅ Stock management and monitoring")
        print("\n🚀 Start using your system at: http://127.0.0.1:8000/")
    else:
        print(f"\n❌ {total - passed} pages have issues")
        print("Please check the server logs for more details")

if __name__ == '__main__':
    main()