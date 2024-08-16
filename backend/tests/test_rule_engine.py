import pytest
import json
from backend.api.ast_utils import create_rule, combine_rules, evaluate_rule, Node
def assert_ast_structure(ast, expected_structure):
    for key, value in expected_structure.items():
        assert key in ast
        if isinstance(value, dict):
            assert_ast_structure(ast[key], value)
        else:
            assert ast[key] == value

def test_create_rule():
    test_cases = [
        {
            "rule": "(age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')",
            "expected": {
                "node_type": "operator",
                "value": "OR",
                "left": {
                    "node_type": "operator",
                    "value": "AND",
                    "left": {"node_type": "operand", "value": "age > 30"},
                    "right": {"node_type": "operand", "value": "department = 'Sales'"}
                },
                "right": {
                    "node_type": "operator",
                    "value": "AND",
                    "left": {"node_type": "operand", "value": "age < 25"},
                    "right": {"node_type": "operand", "value": "department = 'Marketing'"}
                }
            }
        },
        {
            "rule": "experience > 5 AND (salary > 50000 OR position = 'Manager')",
            "expected": {
                "node_type": "operator",
                "value": "AND",
                "left": {"node_type": "operand", "value": "experience > 5"},
                "right": {
                    "node_type": "operator",
                    "value": "OR",
                    "left": {"node_type": "operand", "value": "salary > 50000"},
                    "right": {"node_type": "operand", "value": "position = 'Manager'"}
                }
            }
        },
        {
            "rule": "(location = 'New York' OR location = 'Los Angeles') AND (department = 'IT' OR department = 'HR') AND age >= 25",
            "expected": {
                "node_type": "operator",
                "value": "AND",
                "left": {
                    "node_type": "operator",
                    "value": "AND",
                    "left": {
                        "node_type": "operator",
                        "value": "OR",
                        "left": {"node_type": "operand", "value": "location = 'New York'"},
                        "right": {"node_type": "operand", "value": "location = 'Los Angeles'"}
                    },
                    "right": {
                        "node_type": "operator",
                        "value": "OR",
                        "left": {"node_type": "operand", "value": "department = 'IT'"},
                        "right": {"node_type": "operand", "value": "department = 'HR'"}
                    }
                },
                "right": {"node_type": "operand", "value": "age >= 25"}
            }
        },
        {
            "rule": "years_of_service > 10 OR (salary > 75000 AND performance_rating = 'Excellent')",
            "expected": {
                "node_type": "operator",
                "value": "OR",
                "left": {"node_type": "operand", "value": "years_of_service > 10"},
                "right": {
                    "node_type": "operator",
                    "value": "AND",
                    "left": {"node_type": "operand", "value": "salary > 75000"},
                    "right": {"node_type": "operand", "value": "performance_rating = 'Excellent'"}
                }
            }
        }
    ]

    for case in test_cases:
        result = create_rule(case["rule"])
        result_dict = json.loads(json.dumps(result))

        assert "ast" in result_dict
        assert "message" in result_dict
        assert "rule_id" in result_dict
        assert result_dict["message"] == "Rule created successfully"

        assert_ast_structure(result_dict["ast"], case["expected"])

    # Test invalid rules
    invalid_rules = [
        "invalid rule",
        "age > 30 AND",
        "OR department = 'Sales'",
        "(age > 30)) AND (department = 'Sales'",
    ]

    for invalid_rule in invalid_rules:
        with pytest.raises(ValueError):
            create_rule(invalid_rule)

def test_combine_rules():
    rules = [
        "age > 30 AND department == 'Sales'",
        "experience > 5 OR salary > 50000",
        "age < 25 AND department == 'IT'"
    ]

    combined_rule = combine_rules(rules)

    # Check if the result is a Node
    assert isinstance(combined_rule, Node)

    # Check if the top-level operation is OR (assuming OR is used to combine rules)
    assert combined_rule.operation == "OR"

    # Check if all original rules are present in the combined AST
    def contains_rule(node, rule_string):
        if node is None:
            return False
        if str(node) == rule_string:
            return True
        return contains_rule(node.left, rule_string) or contains_rule(node.right, rule_string)

    for rule in rules:
        assert contains_rule(combined_rule, rule), f"Combined rule should contain: {rule}"

    # Test combining a single rule
    single_rule = ["age > 30"]
    assert str(combine_rules(single_rule)) == "age > 30"

    # Test combining empty list
    assert combine_rules([]) is None

def test_evaluate_rule():
    # Create a sample combined rule
    combined_rule = combine_rules([
        "age > 30 AND department == 'Sales'",
        "experience > 5 OR salary > 50000",
        "age < 25 AND department == 'IT'"
    ])

    # Convert the combined rule to JSON
    rule_json = combined_rule.to_json()

    # Test case 1: Should match the first rule
    data1 = {"age": 35, "department": "Sales", "salary": 45000, "experience": 3}
    assert evaluate_rule(rule_json, data1) == True

    # Test case 2: Should match the second rule
    data2 = {"age": 28, "department": "Marketing", "salary": 55000, "experience": 4}
    assert evaluate_rule(rule_json, data2) == True

    # Test case 3: Should match the third rule
    data3 = {"age": 23, "department": "IT", "salary": 40000, "experience": 1}
    assert evaluate_rule(rule_json, data3) == True

    # Test case 4: Should not match any rule
    data4 = {"age": 28, "department": "HR", "salary": 45000, "experience": 3}
    assert evaluate_rule(rule_json, data4) == False

    # Test case 5: Missing data
    data5 = {"age": 35, "department": "Sales"}
    with pytest.raises(KeyError):
        evaluate_rule(rule_json, data5)

    # Test case 6: Invalid JSON
    with pytest.raises(json.JSONDecodeError):
        evaluate_rule("invalid json", data1)

# Additional test for combining more complex rules
def test_combine_complex_rules():
    complex_rules = [
        "(age > 30 AND department == 'Sales') OR (experience > 5 AND salary > 50000)",
        "education == 'Bachelor' AND (role == 'Manager' OR role == 'Director')",
        "(location == 'New York' OR location == 'San Francisco') AND years_at_company > 2"
    ]

    combined_complex_rule = combine_rules(complex_rules)

    assert isinstance(combined_complex_rule, Node)
    assert combined_complex_rule.operation == "OR"

    # Verify that all original rules are present in the combined AST
    for rule in complex_rules:
        assert str(rule) in str(combined_complex_rule), f"Combined rule should contain: {rule}"

# Test for evaluating a more complex combined rule
def test_evaluate_complex_rule():
    complex_rules = [
        "(age > 30 AND department == 'Sales') OR (experience > 5 AND salary > 50000)",
        "education == 'Bachelor' AND (role == 'Manager' OR role == 'Director')",
        "(location == 'New York' OR location == 'San Francisco') AND years_at_company > 2"
    ]

    combined_complex_rule = combine_rules(complex_rules)
    rule_json = combined_complex_rule.to_json()

    # Should match the first rule
    data1 = {"age": 35, "department": "Sales", "experience": 3, "salary": 45000, 
             "education": "Master", "role": "Associate", "location": "Chicago", "years_at_company": 1}
    assert evaluate_rule(rule_json, data1) == True

    # Should match the second rule
    data2 = {"age": 28, "department": "Marketing", "experience": 6, "salary": 55000, 
             "education": "Bachelor", "role": "Manager", "location": "Dallas", "years_at_company": 1}
    assert evaluate_rule(rule_json, data2) == True

    # Should match the third rule
    data3 = {"age": 25, "department": "IT", "experience": 2, "salary": 40000, 
             "education": "PhD", "role": "Engineer", "location": "New York", "years_at_company": 3}
    assert evaluate_rule(rule_json, data3) == True

    # Should not match any rule
    data4 = {"age": 28, "department": "HR", "experience": 3, "salary": 45000, 
             "education": "Bachelor", "role": "Associate", "location": "Chicago", "years_at_company": 1}
    assert evaluate_rule(rule_json, data4) == False