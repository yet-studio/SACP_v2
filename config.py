CASCADE_CONFIG = {
    'mode': 'premium',
    'memory': {
        'enabled': True,
        'auto_save': {
            'enabled': True,
            'interval': 180,  # 3 minutes
            'max_size': 500_000_000,  # 500MB
            'priority': ['src', 'docs', 'tests'],
            'ignore': ['.git', 'node_modules', '__pycache__', '.pytest_cache']
        },
        'rules_path': '.windsurf_rules'
    },
    'collaboration': {
        'real_time': True,
        'auto_context': {
            'enabled': True,
            'depth': 3,
            'scan_interval': 30,  # 30 secondes
            'max_files': 5000,
            'priority_folders': ['src', 'docs', 'tests']
        }
    }
}
