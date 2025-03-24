import React from 'react';
import ChatRoom from '../components/ChatRoom';
import { useNavigate } from 'react-router-dom';

function ChatPage({ user, roomId }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <header className="bg-blue-500 text-white p-4 flex justify-between items-center">
        <h1 className="text-2xl">Chat Room</h1>
        <button onClick={handleLogout} className="bg-red-500 p-2 rounded hover:bg-red-600 transition duration-200">
          Logout
        </button>
      </header>
      <ChatRoom user={user} roomId={roomId} />
    </div>
  );
}

export default ChatPage;