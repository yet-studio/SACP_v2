"""
Example script to generate a metrics dashboard with realistic validation data.
"""
from src.core.rules_manager import RulesManager
from src.visualization.metrics_dashboard import MetricsDashboard
import os

def generate_sample_validations(rules_manager):
    """Génère des validations d'exemple réalistes."""
    
    # Code samples avec différentes qualités
    code_samples = {
        # Code propre
        "clean_code": """
def calculate_average(numbers):
    \"\"\"Calculate the average of a list of numbers.
    
    Args:
        numbers (List[float]): List of numbers to average
        
    Returns:
        float: The calculated average
        
    Examples:
        >>> calculate_average([1, 2, 3])
        2.0
    \"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
""",
        # Code avec complexité cyclomatique élevée
        "complex_code": """
def process_data(data, options):
    if data is None:
        return None
    
    if options.get('format') == 'json':
        if options.get('validate'):
            if options.get('schema'):
                if validate_schema(data):
                    if options.get('transform'):
                        return transform_json(data)
                    else:
                        return data
                else:
                    return None
            else:
                return data
        else:
            return data
    else:
        return str(data)
""",
        # Code avec problèmes de sécurité
        "unsafe_code": """
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    secret_key = "my_hardcoded_secret_key"
    return execute_query(query)
""",
        # Code avec documentation incomplète
        "poorly_documented": """
def process_transaction(tx):
    if validate(tx):
        result = apply_business_rules(tx)
        if result:
            save_to_db(tx)
            return True
    return False
""",
        # Code avec problèmes de performance
        "inefficient_code": """
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
"""
    }
    
    # Valider chaque exemple avec différentes règles
    for code_type, code in code_samples.items():
        print(f"\nValidating {code_type}...")
        
        # Validation du code
        try:
            result = rules_manager.validate(
                code,
                "method_length",
                context={"type": "code_quality"}
            )
            print(f"Method length validation: {'✓' if result['success'] else '✗'}")
        except Exception as e:
            print(f"Method length validation error: {e}")
        
        # Validation de la complexité
        try:
            result = rules_manager.validate(
                code,
                "cyclomatic_complexity",
                context={"type": "complexity"}
            )
            print(f"Complexity validation: {'✓' if result['success'] else '✗'}")
        except Exception as e:
            print(f"Complexity validation error: {e}")
        
        # Validation de la documentation
        try:
            result = rules_manager.validate(
                code,
                "docstring_completeness",
                context={"type": "documentation"}
            )
            print(f"Documentation validation: {'✓' if result['success'] else '✗'}")
        except Exception as e:
            print(f"Documentation validation error: {e}")
        
        # Validation de la sécurité
        try:
            result = rules_manager.validate(
                code,
                "security_patterns",
                context={"type": "security", "environment": "production"}
            )
            print(f"Security validation: {'✓' if result['success'] else '✗'}")
        except Exception as e:
            print(f"Security validation error: {e}")

def main():
    # Créer le répertoire de sortie
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialiser le système
    rules_manager = RulesManager()
    dashboard = MetricsDashboard(export_dir=output_dir)
    
    # Générer des validations
    print("Generating validation data...")
    generate_sample_validations(rules_manager)
    
    # Créer le dashboard
    print("\nGenerating dashboard...")
    dashboard.update_dashboard(rules_manager)
    
    print("\nDashboard generated in:", output_dir)
    print("Open the latest dashboard_*.html file in your browser to view the metrics.")

if __name__ == "__main__":
    main()
