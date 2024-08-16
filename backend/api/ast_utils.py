# backend/app/ast_utils.py
import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # "operator" for AND/OR, "operand" for conditions
        self.left = left
        self.right = right
        self.value = value

def tokenize_rule(rule_string):
    # Use regex to tokenize the rule string, splitting on spaces, parentheses, and operators.
    tokens = re.findall(r'\(|\)|AND|OR|<=|>=|!=|>|<|=|\'[^\']*\'|\w+', rule_string)
    return tokens

def precedence(op):
    if op == "AND":
        return 2
    if op == "OR":
        return 1
    return 0

def apply_operator(operators, operands):
    op = operators.pop()
    right = operands.pop()
    left = operands.pop()
    node = Node(node_type="operator", left=left, right=right, value=op)
    operands.append(node)


def create_rule(rule_string):
    tokens = tokenize_rule(rule_string)
    operators = []  # Stack for operators (AND/OR)
    operands = []  # Stack for operands (conditions)
    
    # Temporary variables for building full conditions
    current_operand = []

    for token in tokens:
        if token == '(':
            operators.append(token)
        elif token == ')':
            if current_operand:
                # Join the current operand to form a complete condition
                operands.append(Node(node_type="operand", value=" ".join(current_operand)))
                current_operand = []
            
            # Pop operators until we find a '('
            while operators and operators[-1] != '(':
                apply_operator(operators, operands)
            operators.pop()  # Discard the '('
        elif token in ('AND', 'OR'):
            if current_operand:
                # Join the current operand to form a complete condition
                operands.append(Node(node_type="operand", value=" ".join(current_operand)))
                current_operand = []
            
            # Handle operator precedence
            while (operators and operators[-1] != '(' and
                   precedence(operators[-1]) >= precedence(token)):
                apply_operator(operators, operands)
            operators.append(token)
        else:
            # Build the current operand (e.g., 'age > 30')
            current_operand.append(token)
    
    # Final check for remaining operand
    if current_operand:
        operands.append(Node(node_type="operand", value=" ".join(current_operand)))

    # Apply remaining operators
    while operators:
        apply_operator(operators, operands)

    # The final element in the operands stack is the root of the AST
    return operands.pop()


def combine_rules(rules):
    if not rules:
        return None
    root = None
    for rule in rules:
        ast = create_rule(rule)
        if root is None:
            root = ast
        else:
            root = Node(node_type="operator", left=root, right=ast, value="AND")
    return root

def evaluate_node(node, data):
    if node.type == "operand":
        attribute, operator, value = node.value.split()
        attribute_value = data.get(attribute)

        if operator == '>':
            return attribute_value > int(value)
        elif operator == '<':
            return attribute_value < int(value)
        elif operator == '=':
            return attribute_value == value
        elif operator == '!=':
            return attribute_value != value
        else:
            raise ValueError("Invalid operator")

    elif node.type == "operator":
        left_val = evaluate_node(node.left, data)
        right_val = evaluate_node(node.right, data)

        if node.value == "AND":
            return left_val and right_val
        elif node.value == "OR":
            return left_val or right_val
        else:
            raise ValueError("Invalid operator")
    
    return False

def deserialize_ast(ast_data):
    if ast_data is None:
        return None

    node_type = ast_data.get('node_type')
    value = ast_data.get('value')
    
    left = deserialize_ast(ast_data.get('left'))  
    right = deserialize_ast(ast_data.get('right'))  
    return Node(node_type=node_type, left=left, right=right, value=value)

def evaluate_rule(ast, data):
    return evaluate_node(ast, data)
