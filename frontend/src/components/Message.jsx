import React from 'react';

function Message({ message }) {
  return (
    <div className="flex items-start mb-4">
      <img src={`https://api.adorable.io/avatars/40/${message.sender.id}.png`} alt={`${message.sender.name}'s avatar`} className="w-10 h-10 rounded-full mr-3" />
      <div>
        <div className="text-sm text-gray-500">{message.sender.name}</div>
        <div className="bg-gray-200 p-2 rounded-lg">
          <p className="text-gray-800">{message.content}</p>
          <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}

export default Message;