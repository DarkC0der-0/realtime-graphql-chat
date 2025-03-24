import React, { useState } from 'react';
import { ApolloProvider } from '@apollo/client';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { client } from './utils/graphql';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import PrivateRoute from './components/PrivateRoute';

function App() {
  const [user, setUser] = useState(null);

  return (
    <ApolloProvider client={client}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage onLogin={setUser} />} />
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <ChatPage user={user} roomId={1} />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </ApolloProvider>
  );
}

export default App;