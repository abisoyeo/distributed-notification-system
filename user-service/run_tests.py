#!/usr/bin/env python
"""
Quick test runner script for User Service
Usage: python run_tests.py [options]
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run tests with Django test runner"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Build test command
    args = ['manage.py', 'test'] + sys.argv[1:]
    
    # Add default options if none provided
    if len(sys.argv) == 1:
        args.extend(['--verbosity=2', '--keepdb'])
    
    print("="*80)
    print("Running User Service Test Suite")
    print("="*80)
    print(f"Command: {' '.join(args)}")
    print("="*80 + "\n")
    
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
