#!/usr/bin/env python3
"""
Script to initialize the LLM context configuration.
Creates llm_context.yaml from llm_context.default.yaml if it doesn't exist.
"""
import shutil
from pathlib import Path

def setup_config():
    """Initialize the LLM context configuration."""
    config_dir = Path(__file__).parent.parent / 'config'
    default_config = config_dir / 'llm_context.default.yaml'
    instance_config = config_dir / 'llm_context.yaml'
    
    # Vérifier si le fichier de configuration par défaut existe
    if not default_config.exists():
        print(f"Error: Default configuration file not found: {default_config}")
        return False
    
    # Ne pas écraser la configuration existante
    if instance_config.exists():
        print(f"Instance configuration already exists: {instance_config}")
        print("Edit this file to customize your settings.")
        return True
    
    # Copier le fichier de configuration par défaut
    try:
        shutil.copy2(default_config, instance_config)
        print(f"Created instance configuration: {instance_config}")
        print("Edit this file to customize your settings.")
        return True
    except Exception as e:
        print(f"Error creating instance configuration: {e}")
        return False

if __name__ == '__main__':
    setup_config()
