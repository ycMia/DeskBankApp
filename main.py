#!/usr/bin/env python3
"""
DeskBank Application - Main Entry Point

A modular banking application with proper separation of concerns.
"""

import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from deskbank.app import DeskBankApp


def main():
    """Main entry point for the DeskBank application."""
    parser = argparse.ArgumentParser(
        description="DeskBank - Modern Banking Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with CLI interface
  python main.py --ui GUI           # Run with GUI interface (if available)
  python main.py --config config.json  # Run with custom configuration
  python main.py --help             # Show this help message

Default credentials:
  Manager: username='admin', password='admin123'
        """
    )
    
    parser.add_argument(
        "--ui",
        choices=["CLI", "GUI"],
        default="CLI",
        help="User interface type (default: CLI)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="DeskBank v1.0.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    try:
        args = parser.parse_args()
        
        # Display startup banner
        print_banner()
        
        # Create and run application
        app = DeskBankApp(
            ui_type=args.ui,
            config_file=args.config
        )
        
        if args.debug:
            print("Debug mode enabled")
            print(f"System info: {app.get_system_info()}")
        
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        if args.debug if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_banner():
    """Print application startup banner."""
    banner = """
    ██████╗ ███████╗███████╗██╗  ██╗██████╗  █████╗ ███╗   ██╗██╗  ██╗
    ██╔══██╗██╔════╝██╔════╝██║ ██╔╝██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝
    ██║  ██║█████╗  ███████╗█████╔╝ ██████╔╝███████║██╔██╗ ██║█████╔╝ 
    ██║  ██║██╔══╝  ╚════██║██╔═██╗ ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ 
    ██████╔╝███████╗███████║██║  ██╗██████╔╝██║  ██║██║ ╚████║██║  ██╗
    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                              Your Trusted Banking Partner
    
    🏦 Welcome to DeskBank - Modern Banking Application
    📋 Version: 1.0.0
    🏗️  Architecture: Modular MVC with Clean Architecture
    🔒 Security: SHA-256 Password Hashing & Session Management
    """
    print(banner)


if __name__ == "__main__":
    main()