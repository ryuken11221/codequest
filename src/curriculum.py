"""
curriculum.py — 30-day curriculum definitions for CodeQuest 2.
Each day has: number, title, goal, concept, task, xp.
"""

DAYS = [
    {"n": 1,  "title": "Hello, World", "goal": "Setup + first run", "concept": "print, comments, REPL", "task": "Print a greeting with your name. Then print a 3-line ASCII art of a spaceship.", "xp": 50},
    {"n": 2,  "title": "Variables & types", "goal": "Data storage", "concept": "int, float, str, bool, None", "task": "Store your age, height, and favorite food in variables. Print them with type() labels.", "xp": 50},
    {"n": 3,  "title": "User input", "goal": "Interactivity", "concept": "input(), type conversion", "task": "Build a mini calculator: ask for two numbers and an operator (+,-,*,/), print the result.", "xp": 60},
    {"n": 4,  "title": "Conditionals", "goal": "Branching logic", "concept": "if/elif/else, comparison ops", "task": "Write a program that classifies a temperature: freezing/cold/cool/comfortable/warm/hot. Test with 5 values.", "xp": 60},
    {"n": 5,  "title": "Loops I", "goal": "Repetition", "concept": "while, range, break, continue", "task": "Print the multiplication table (1-10) for a user-chosen number using nested loops.", "xp": 60},
    {"n": 6,  "title": "Strings", "goal": "Text manipulation", "concept": "slicing, .split, .join, .format, f-strings", "task": "Write a palindrome checker and a word-frequency counter for a user-entered sentence.", "xp": 70},
    {"n": 7,  "title": "Lists", "goal": "Collections", "concept": "list methods, indexing, list comprehensions", "task": "Build a to-do list: add, remove, mark done, show all. Use only list methods (no sets).
