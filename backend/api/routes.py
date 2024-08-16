# backend/app/routes.py

from .ast_utils import Node
from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # type: ignore
from .ast_utils import *
import json
#from .ast_utils import create_rule, combine_rules, evaluate_rule

app = Flask(__name__)
CORS(app)
# Configuring the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:siva@localhost/rule_engine_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database connection
db = SQLAlchemy(app)

# Define the Rule model to store individual rules
class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    rule_string = db.Column(db.Text, nullable=False)
    ast = db.Column(db.JSON, nullable=False)

# Define the CombinedRule model to store combined rules
class CombinedRule(db.Model):
    __tablename__ = 'combined_rules'
    id = db.Column(db.Integer, primary_key=True)
    combined_rule_string = db.Column(db.Text, nullable=False)
    combined_ast = db.Column(db.JSON, nullable=False)

@app.route('/rules', methods=['GET'])
def get_rules():
    rules = Rule.query.all()
    rules_list = [{"id": rule.id, "rule_string": rule.rule_string, "ast": rule.ast} for rule in rules]
    return jsonify(rules=rules_list), 200

@app.route('/combined_rules', methods=['GET'])
def get_combined_rules():
    combined_rules = CombinedRule.query.all()
    combined_rules_list = [{"id": cr.id, "combined_rule_string": cr.combined_rule_string, "combined_ast": cr.combined_ast} for cr in combined_rules]
    return jsonify(combined_rules=combined_rules_list), 200


@app.route('/create_rule', methods=['POST'])
def create_rule_endpoint():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    rule_string = data.get('rule_string')
    if not rule_string:
        return jsonify({"error": "rule_string is required"}), 400
    
    ast = create_rule(rule_string)
    def ast_to_dict(node):
        if node is None:
            return None

        return {
            "node_type": node.type,
            "value": node.value,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right)
        }
    # Save the rule and AST to the database
    new_rule = Rule(rule_string=rule_string, ast=ast_to_dict(ast))
    db.session.add(new_rule)
    db.session.commit()

    return jsonify({
            "message": "Rule created successfully",
            "rule_id": new_rule.id,
            "ast": ast_to_dict(ast)
        }), 200  # Convert Node to dictionary for JSON


@app.route('/combine_rules', methods=['POST'])
def combine_rules_endpoint():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Get the list of rule IDs from the incoming data
    rule_ids = data.get('rules')

    # Check if rule_ids is present and convert to list if it's a string
    if isinstance(rule_ids, str):
        rule_ids = rule_ids.split(',')

    # Ensure rule_ids is a list
    if not rule_ids or not isinstance(rule_ids, list):
        return jsonify({"error": "rule_ids is required and should be a list"}), 400

    # Convert rule IDs to integers
    try:
        rule_ids = [int(rule_id.strip()) for rule_id in rule_ids]
    except ValueError:
        return jsonify({"error": "rule_ids must be integers"}), 400

    # Fetch the corresponding rules from the database
    rules = [rule.rule_string for rule in Rule.query.filter(Rule.id.in_(rule_ids)).all()]

    if not rules:
        return jsonify({"error": "No valid rules found for the given IDs"}), 400

    # Call the combine_rules function with the list of rules
    combined_ast = combine_rules(rules)

    # Convert the AST to a dictionary to save it in the database
    def ast_to_dict(node):
        if node is None:
            return None

        return {
            "node_type": node.type,
            "value": node.value,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right)
        }

    # Save the combined rule and AST to the database
    new_combined_rule = CombinedRule(
        combined_rule_string=" AND ".join(rules),
        combined_ast=ast_to_dict(combined_ast)
    )
    db.session.add(new_combined_rule)
    db.session.commit()

    return jsonify(ast=ast_to_dict(combined_ast)), 200

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_endpoint():
    if request.is_json:
        data = request.get_json()
        ast_data = data.get('ast')
        data1 = data.get('data')
    else:
        # If the request is form data (HTML form submission)
        data = request.form
        ast_data_str = data.get('ast')
        data1_str = data.get('data')
        if ast_data_str:
            try:
                ast_data = json.loads(ast_data_str)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid AST data"}), 400
        else:
            ast_data = None
        if data1_str:
            try:
                data1 = json.loads(data1_str)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid data"}), 400
        else:
            data1 = None

    if ast_data:
        # Deserialize AST
        ast = deserialize_ast(ast_data)
        
        result = evaluate_rule(ast, data1)
    
        return jsonify(result=result), 200
    else:
        return jsonify({"error": "No AST data provided"}), 400
    

def new_func(app, db):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    new_func(app, db)
    app.run(debug=True)
