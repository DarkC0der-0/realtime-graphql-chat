import { gql } from '@apollo/client';

export const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    authLogin(email: $email, password: $password) {
      accessToken
      user {
        id
        name
      }
    }
  }
`;

export const CREATE_MESSAGE_MUTATION = gql`
  mutation CreateMessage($content: String!, $userId: Int!, $roomId: Int!) {
    createMessage(content: $content, userId: $userId, roomId: $roomId) {
      message {
        id
        content
        sender {
          id
          name
        }
      }
    }
  }
`;

export const MESSAGES_SUBSCRIPTION = gql`
  subscription OnMessageCreated($roomId: Int!) {
    messageCreated(roomId: $roomId) {
      id
      content
      sender {
        id
        name
      }
    }
  }
`;

export const FETCH_MESSAGES_QUERY = gql`
  query FetchMessages($roomId: Int!, $first: Int, $after: String) {
    messagesByRoom(roomId: $roomId, first: $first, after: $after) {
      edges {
        cursor
        node {
          id
          content
          timestamp
          sender {
            id
            name
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
`;