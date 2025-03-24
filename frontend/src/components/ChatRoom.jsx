import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useSubscription, useMutation } from '@apollo/client';
import { FETCH_MESSAGES_QUERY, MESSAGES_SUBSCRIPTION, CREATE_MESSAGE_MUTATION } from '../utils/queries';
import Message from './Message';

const PAGE_SIZE = 20;

function ChatRoom({ user, roomId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [fetchingMore, setFetchingMore] = useState(false);
  const { data: queryData, loading: queryLoading, error: queryError, fetchMore } = useQuery(FETCH_MESSAGES_QUERY, {
    variables: { roomId, first: PAGE_SIZE, after: null },
    notifyOnNetworkStatusChange: true,
  });
  const { data: subscriptionData, error: subscriptionError } = useSubscription(MESSAGES_SUBSCRIPTION, { variables: { roomId } });
  const [createMessage] = useMutation(CREATE_MESSAGE_MUTATION);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (queryData) {
      setMessages(queryData.messagesByRoom.edges.map(edge => edge.node));
    }
  }, [queryData]);

  useEffect(() => {
    if (subscriptionData) {
      setMessages(prevMessages => [...prevMessages, subscriptionData.messageCreated]);
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [subscriptionData]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    await createMessage({ variables: { content: newMessage, userId: user.id, roomId } });
    setNewMessage('');
  };

  const handleFetchMore = async () => {
    const { endCursor } = queryData.messagesByRoom.pageInfo;
    setFetchingMore(true);
    await fetchMore({
      variables: { roomId, first: PAGE_SIZE, after: endCursor },
      updateQuery: (prevResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.messagesByRoom.edges;
        const pageInfo = fetchMoreResult.messagesByRoom.pageInfo;
        return {
          messagesByRoom: {
            __typename: prevResult.messagesByRoom.__typename,
            edges: [...newEdges, ...prevResult.messagesByRoom.edges],
            pageInfo,
          },
        };
      },
    });
    setFetchingMore(false);
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {queryLoading && <p>Loading messages...</p>}
        {queryError && <p>Error loading messages: {queryError.message}</p>}
        {subscriptionError && <p>Error with WebSocket connection: {subscriptionError.message}</p>}
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
        {queryData && queryData.messagesByRoom.pageInfo.hasNextPage && (
          <button
            onClick={handleFetchMore}
            disabled={fetchingMore}
            className="w-full bg-gray-200 text-gray-700 p-2 rounded mt-4"
          >
            {fetchingMore ? 'Loading more...' : 'Load More'}
          </button>
        )}
      </div>
      <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-300">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded"
          placeholder="Type your message..."
        />
      </form>
    </div>
  );
}

export default ChatRoom;