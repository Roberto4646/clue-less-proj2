from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brian_san'
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")  # Allow requests from the frontend


# Game state variables
players = {}
games = {}

class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.status = "waiting" 
        self.board = {
            'rooms': ['Kitchen', 'Library', 'Conservatory', 'Hall', 'Study', 'Dining Room'],
            'weapons': ['Knife', 'Candlestick', 'Revolver', 'Rope', 'Lead Pipe', 'Wrench'],
            'characters': ['Miss Scarlett', 'Colonel Mustard', 'Mrs. White', 'Mr. Green', 'Mrs. Peacock', 'Professor Plum']
        }
        self.players = []

    def add_player(self, player_id):
        self.players.append(player_id)

    def start_game(self):
        self.status = "started"

    def move_player(self, player_id, room):
        if player_id != self.current_player:
            return False, "It's not your turn"
        
        # Implement player movement logic here
        if room in self.board['rooms']:
            # Update player position
            # Example: self.players[player_id].position = room
            # Emit event to inform players about the movement
            emit('player_moved', {'player_id': player_id, 'room': room}, room=player_id)
            return True, f"Moved to {room} successfully"
        else:
            return False, "Invalid room"

    def make_suggestion(self, player_id, room, suspect, weapon):
        if player_id != self.current_player:
            return False, "It's not your turn"
        
        # Implement suggestion logic here
        if room in self.board['rooms'] and suspect in self.board['characters'] and weapon in self.board['weapons']:
            # Check if any player can disprove the suggestion
            # Example: self.check_disprove(player_id, room, suspect, weapon)
            # Emit event to inform players about the suggestion
            emit('suggestion_made', {'player_id': player_id, 'room': room, 'suspect': suspect, 'weapon': weapon}, room=player_id)
            return True, "Suggestion made successfully"
        else:
            return False, "Invalid suggestion"

    def handle_accusation(self, player_id, suspect, weapon, room):
        if player_id != self.current_player:
            return False, "It's not your turn"
        
        # Implement accusation logic here
        if suspect == 'Correct_Suspect' and weapon == 'Correct_Weapon' and room == 'Correct_Room':
            # Emit event to inform players about the correct accusation
            emit('accusation_correct', {'player_id': player_id, 'suspect': suspect, 'weapon': weapon, 'room': room}, room=player_id)
            return True, "Congratulations! Your accusation was correct"
        else:
            # Emit event to inform players about the incorrect accusation
            emit('accusation_incorrect', {'player_id': player_id, 'suspect': suspect, 'weapon': weapon, 'room': room}, room=player_id)
            return False, "Incorrect accusation"

# WebSocket Integration
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Handle Player Actions
@app.route('/move', methods=['POST'])
def handle_move():
    data = request.json
    player_id = data['player_id']
    room = data['room']
    game_id = data['game_id']
    games[game_id].move_player(player_id, room)
    return jsonify({'message': 'Player moved successfully'})

@app.route('/suggest', methods=['POST'])
def handle_suggest():
    data = request.json
    player_id = data['player_id']
    room = data['room']
    suspect = data['suspect']
    weapon = data['weapon']
    game_id = data['game_id']
    games[game_id].make_suggestion(player_id, room, suspect, weapon)
    return jsonify({'message': 'Suggestion made successfully'})

@app.route('/accuse', methods=['POST'])
def handle_accuse():
    data = request.json
    player_id = data['player_id']
    suspect = data['suspect']
    weapon = data['weapon']
    room = data['room']
    game_id = data['game_id']
    games[game_id].handle_accusation(player_id, suspect, weapon, room)
    return jsonify({'message': 'Accusation handled successfully'})

# Manage multiple game instances for each group of players
@app.route('/create_game', methods=['POST'])
def create_game():
    game_id = len(games) + 1
    games[game_id] = Game(game_id)
    return jsonify({'game_id': game_id})

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    game_id = data['game_id']
    game = games.get(game_id)
    if game:
        game.start_game()
        return jsonify({'message': 'Game started successfully'})
    else:
        return jsonify({'error': 'Game not found'})

@app.route('/players/<int:game_id>', methods=['GET'])
def get_players(game_id):
    game = games.get(game_id)
    if game:
        return jsonify({'players': game.players})
    else:
        return jsonify({'error': 'Game not found'})

@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    game_id = data['game_id']
    player_id = data['player_id']
    games[game_id].players.append(player_id)
    return jsonify({'message': 'Player joined game'})

if __name__ == '__main__':
    socketio.run(app)
