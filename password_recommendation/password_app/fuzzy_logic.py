import random
import skfuzzy as fuzz
import numpy as np
from skfuzzy import control as ctrl

# Input variables
length = ctrl.Antecedent(np.arange(0, 26, 1), 'length')
complexity = ctrl.Antecedent(np.arange(2, 13, 1), 'complexity')

# Output variable for Password Strength
strength = ctrl.Consequent(np.arange(0, 101, 1), 'strength')

# Membership functions for length
length['very_short'] = fuzz.trimf(length.universe, [0, 0, 5])
length['short'] = fuzz.trimf(length.universe, [5, 5, 10])
length['medium'] = fuzz.trimf(length.universe, [10, 10, 15])
length['long'] = fuzz.trimf(length.universe, [15, 15, 20])
length['very_long'] = fuzz.trimf(length.universe, [20, 25, 25])

# Membership functions for complexity
complexity['very_low'] = fuzz.trimf(complexity.universe, [2, 2, 4])
complexity['low'] = fuzz.trimf(complexity.universe, [4, 4, 6])
complexity['medium'] = fuzz.trimf(complexity.universe, [6, 6, 8])
complexity['high'] = fuzz.trimf(complexity.universe, [8, 8, 10])
complexity['very_high'] = fuzz.trimf(complexity.universe, [10, 12, 12])

# Membership functions for strength
strength['very_weak'] = fuzz.trimf(strength.universe, [0, 0, 25])
strength['weak'] = fuzz.trimf(strength.universe, [0, 25, 50])
strength['moderate'] = fuzz.trimf(strength.universe, [25, 50, 75])
strength['strong'] = fuzz.trimf(strength.universe, [50, 75, 100])
strength['very_strong'] = fuzz.trimf(strength.universe, [75, 100, 100])

# Define the fuzzy rules

rule1 = ctrl.Rule(complexity['very_low'] & length['very_short'], strength['very_weak'])
rule2 = ctrl.Rule(complexity['low'] & length['very_short'], strength['weak'])
rule3 = ctrl.Rule(complexity['medium'] & length['very_short'], strength['weak'])
rule4 = ctrl.Rule(complexity['high'] & length['very_short'], strength['weak'])
rule5 = ctrl.Rule(complexity['very_high'] & length['very_short'], strength['moderate'])

rule6 = ctrl.Rule(complexity['very_low'] & length['short'], strength['weak'])
rule7 = ctrl.Rule(complexity['low'] & length['short'], strength['weak'])
rule8 = ctrl.Rule(complexity['medium'] & length['short'], strength['moderate'])
rule9 = ctrl.Rule(complexity['high'] & length['short'], strength['moderate'])
rule10 = ctrl.Rule(complexity['very_high'] & length['short'], strength['strong'])

rule11 = ctrl.Rule(complexity['very_low'] & length['medium'], strength['weak'])
rule12 = ctrl.Rule(complexity['low'] & length['medium'], strength['moderate'])
rule13 = ctrl.Rule(complexity['medium'] & length['medium'], strength['moderate'])
rule14 = ctrl.Rule(complexity['high'] & length['medium'], strength['strong'])
rule15 = ctrl.Rule(complexity['very_high'] & length['medium'], strength['strong'])

rule16 = ctrl.Rule(complexity['very_low'] & length['long'], strength['moderate'])
rule17 = ctrl.Rule(complexity['low'] & length['long'], strength['moderate'])
rule18 = ctrl.Rule(complexity['medium'] & length['long'], strength['strong'])
rule19 = ctrl.Rule(complexity['high'] & length['long'], strength['strong'])
rule20 = ctrl.Rule(complexity['very_high'] & length['long'], strength['very_strong'])

rule21 = ctrl.Rule(complexity['very_low'] & length['very_long'], strength['moderate'])
rule22 = ctrl.Rule(complexity['low'] & length['very_long'], strength['strong'])
rule23 = ctrl.Rule(complexity['medium'] & length['very_long'], strength['strong'])
rule24 = ctrl.Rule(complexity['high'] & length['very_long'], strength['very_strong'])
rule25 = ctrl.Rule(complexity['very_high'] & length['very_long'], strength['very_strong'])

# Control system creation and simulation
strength_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5,
                                    rule6, rule7, rule8, rule9, rule10,
                                    rule11, rule12, rule13, rule14, rule15,
                                    rule16, rule17, rule18, rule19, rule20,
                                    rule21, rule22, rule23, rule24, rule25])

strength_simulation = ctrl.ControlSystemSimulation(strength_ctrl)

def evaluate_password_strength(length_input, complexity_input):
    # Input values
    strength_simulation.input['length'] = length_input
    strength_simulation.input['complexity'] = complexity_input
    
    # Compute the result
    strength_simulation.compute()
    
    # Return the defuzzified output
    return strength_simulation.output['strength']

# Membership Functions
def membership_functions():
    x_strength = np.arange(0, 11, 1)

    weak = fuzz.trimf(x_strength, [0, 0, 5])
    moderate = fuzz.trimf(x_strength, [3, 5, 8])
    strong = fuzz.trimf(x_strength, [6, 10, 10])

    return x_strength, weak, moderate, strong

# Fuzzy Rule Evaluation
def evaluate_rules(length, complexity, diversity):
    x_strength, weak, moderate, strong = membership_functions()

    # Fuzzification
    length_level = fuzz.interp_membership(x_strength, strong, length)
    complexity_level = fuzz.interp_membership(x_strength, strong, complexity)
    diversity_level = fuzz.interp_membership(x_strength, strong, diversity)

    # Applying Fuzzy Rules
    weak_level = min(length_level, complexity_level, diversity_level)
    moderate_level = np.mean([length_level, complexity_level, diversity_level])
    strong_level = max(length_level, complexity_level, diversity_level)

    # Defuzzification (we'll use the centroid method)
    password_strength = fuzz.defuzz(x_strength, np.fmax(weak, np.fmax(moderate, strong)), 'centroid')

    return password_strength

# Password Generation
def generate_password(info):
    words = [info['name'], info['maiden_name'], info['nickname'], info['profession']]
    random.shuffle(words)
    password = ''.join([word[:random.randint(2, 4)] for word in words])
    password += str(random.randint(10, 99))  # Adding numbers for complexity
    password = ''.join(random.sample(password, len(password)))  # Shuffling characters for diversity

    return password

# Determine Complexity and Diversity
def evaluate_complexity(password):
    length = len(password)
    diversity = len(set(password))
    complexity = sum([1 for char in password if char.isdigit()]) + sum([1 for char in password if not char.isalnum()])

    return length, complexity, diversity

# Main function to run the system
def password_recommendation_system(info):
    password = generate_password(info)
    length, complexity, diversity = evaluate_complexity(password)
    strength = evaluate_rules(length, complexity, diversity)

    if strength >= 7:
        strength_label = "Strong"
    elif strength >= 4:
        strength_label = "Moderate"
    else:
        strength_label = "Weak"

    return password, strength_label

# Example Usage
info = {
    'name': 'JohnDoe',
    'date_of_birth': '1990-01-01',
    'maiden_name': 'Smith',
    'nickname': 'Johnny',
    'gender': 'Male',
    'religion' : 'Christian',
    'profession': 'Engineer',
    'complexion': 'Fair'
}

password, strength_label = password_recommendation_system(info)
print(f"Recommended Password: {password}")
print(f"Password Strength: {strength_label}")
