#!/usr/bin/env python3
"""
Authentication Setup Script
Run this to generate proper password hashes for authentication
"""

import streamlit_authenticator as stauth
from pathlib import Path
import yaml


def generate_auth_config():
    """Generate authentication configuration with proper password hashes"""

    # Generate password hashes
    passwords = ['demo123', 'admin123', 'john123', 'jane123']
    hashed_passwords = stauth.Hasher(passwords).generate()

    config = {
        'credentials': {
            'usernames': {
                'demo_user': {
                    'email': 'demo@example.com',
                    'name': 'Demo User',
                    'password': hashed_passwords[0]
                },
                'admin': {
                    'email': 'admin@example.com',
                    'name': 'Administrator',
                    'password': hashed_passwords[1]
                },
                'john_doe': {
                    'email': 'john@example.com',
                    'name': 'John Doe',
                    'password': hashed_passwords[2]
                },
                'jane_smith': {
                    'email': 'jane@example.com',
                    'name': 'Jane Smith',
                    'password': hashed_passwords[3]
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'stock_market_analyzer_key_2024',
            'name': 'stock_market_analyzer_cookie'
        },
        'preauthorized': {
            'emails': ['admin@example.com']
        }
    }

    # Create config directory
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)

    # Save configuration
    config_file = config_dir / 'auth_config.yaml'
    with open(config_file, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

    print(f"✅ Authentication configuration saved to: {config_file}")
    print("\n🔐 Demo User Credentials:")
    print("Username: demo_user | Password: demo123")
    print("Username: admin     | Password: admin123")
    print("Username: john_doe  | Password: john123")
    print("Username: jane_smith| Password: jane123")
    print("\n🎯 Each user will have their own separate portfolio!")


if __name__ == "__main__":
    generate_auth_config()