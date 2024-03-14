import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';

const socket = io('http://localhost:5000');

function App() {
  const [gameId, setGameId] = useState(null);
  const [players, setPlayers] = useState([]);
  const [status, setStatus] = useState('');

  useEffect(() => {
    // Listen for socket events
    socket.on('connect', () => console.log('Connected to server'));
    socket.on('disconnect', () => console.log('Disconnected from server'));

    return () => {
      // Clean up socket listeners
      socket.off('connect');
      socket.off('disconnect');
    };
  }, []);

  const createGame = async () => {
    try {
      const response = await axios.post('http://localhost:5000/create_game');
      const { game_id } = response.data;
      setGameId(game_id);
      setStatus('Waiting for players...');
    } catch (error) {
      console.error('Error creating game:', error);
    }
  };  

  const startGame = async () => {
    try {
      await axios.post('http://localhost:5000/start_game', { game_id: gameId });
      setStatus('Game started!');
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };

  const joinGame = async () => {
    const player_id = prompt('Enter your player ID:');
    try {
      await axios.post('http://localhost:5000/join_game', { game_id: gameId, player_id });
      setPlayers([...players, player_id]);
    } catch (error) {
      console.error('Error joining game:', error);
    }
  };

  const getPlayers = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/players/${gameId}`);
      const { players } = response.data;
      setPlayers(players);
    } catch (error) {
      console.error('Error getting players:', error);
    }
  };

  return (
    <div>
      <h1>Clue-less Game</h1>
      <button onClick={createGame}>Create Game</button>
      <button onClick={startGame} disabled={!gameId}>Start Game</button>
      <button onClick={joinGame} disabled={!gameId}>Join Game</button>
      <button onClick={getPlayers} disabled={!gameId}>Get Players</button>
      <h2>Game Status: {status}</h2>
      <h2>Players:</h2>
      <ul>
        {players.map((player, index) => (
          <li key={index}>{player}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
