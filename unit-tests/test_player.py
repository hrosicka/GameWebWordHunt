# GameWebWord Hunt> python -m unittest unit-tests/test_player.py

import unittest
import json
from pathlib import Path
from routes.player import load_scores, save_scores, player_bp  # Předpokládám, že player.py je v balíčku your_package_name
from routes.game import game_bp
from flask import Flask
from flask.testing import FlaskClient

class TestPlayerFunctions(unittest.TestCase):

    def setUp(self):
        """Nastavení před každým testem."""
        self.app = Flask(__name__, template_folder='../templates')
        self.app.config['SCORE_FILE'] = 'test_scores.json'
        self.app.config['SECRET_KEY'] = 'your_secret_key'
        self.app.words_with_clues = {"test": ["clue1"]}
        self.app.register_blueprint(game_bp)
        self.app.register_blueprint(player_bp)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Úklid po každém testu."""
        Path('test_scores.json').unlink(missing_ok=True)
        Path('test_save.json').unlink(missing_ok=True)
        Path('invalid.json').unlink(missing_ok=True)
        Path('test_update_guest.json').unlink(missing_ok=True)
        Path('test_update_no_guest.json').unlink(missing_ok=True)
        self.app_context.pop()

    def test_load_scores_existing_file(self):
        # Define the test data representing player scores
        test_data = {"player_scores": {"Monica": 100, "Robert": 50}}
        # Open a file named 'test_scores.json' in write mode ('w')
        with open('test_scores.json', 'w') as f:
            # Dump the test_data into the file as JSON
            json.dump(test_data, f)
        # Call the load_scores function with the path to the created file
        scores = load_scores('test_scores.json')
        # Assert that the scores loaded from the file are equal to the original test_data
        self.assertEqual(scores, test_data)

    def test_load_scores_non_existing_file(self):
        # Call the load_scores function with a path to a non-existent file
        scores = load_scores('non_existent.json')
        # Assert that the function returns the expected default dictionary for a non-existent file
        self.assertEqual(scores, {"player_scores": {}})

    def test_load_scores_invalid_json(self):
        # Open a file named 'invalid.json' in write mode ('w')
        with open('invalid.json', 'w') as f:
            # Write a string that is not valid JSON to the file
            f.write('not a json')
        # Call the load_scores function with the path to the file containing invalid JSON
        scores = load_scores('invalid.json')
        # Assert that the function returns the expected default dictionary when the JSON is invalid
        self.assertEqual(scores, {"player_scores": {}})

    def test_save_scores(self):
        # Define the test data to be saved
        test_data = {"player_scores": {"Charlie": 200}}
        # Call the save_scores function to save the test data to a file named 'test_save.json'
        save_scores('test_save.json', test_data)
        # Open the same file in read mode ('r') to load the data that was just saved
        with open('test_save.json', 'r') as f:
            # Load the JSON data from the file
            loaded_data = json.load(f)
        # Assert that the loaded data is equal to the original test data, verifying the save operation
        self.assertEqual(loaded_data, test_data)

    def test_change_name_get(self):
        response = self.client.get('/player/change_name')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

        # Check for the presence of key texts and elements
        self.assertIn(b'Change Player Name', response.data)
        self.assertIn(b'<form method="POST" action="/player/change_name">', response.data)
        self.assertIn(b'<label for="selected-player">Select Existing:</label>', response.data)
        self.assertIn(b'<select id="selected-player" name="selected_player">', response.data)
        self.assertIn(b'<option value="">-- Select Player --</option>', response.data)
        self.assertIn(b'<label for="new-player-name">Or Enter New:</label>', response.data)
        self.assertIn(b'<input type="text" id="new-player-name" name="new_player_name"', response.data)
        self.assertIn(b'<button type="submit">Save</button>', response.data)
        self.assertIn(b'<button type="button" class="back-button"', response.data)
        self.assertIn(b'Back to Game</button>', response.data)

    def test_get_player_default(self):
            # Send a GET request to the '/player/get' endpoint
            response = self.client.get('/player/get')
            # Assert that the HTTP status code of the response is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Assert that the JSON content of the response is a dictionary
            # with the key 'player' and the value 'Guest', which is the default player name
            self.assertEqual(response.get_json(), {'player': 'Guest'})

if __name__ == '__main__':
    unittest.main()