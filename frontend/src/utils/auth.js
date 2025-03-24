import { gql } from '@apollo/client';
import { client } from './graphql';

const LOGIN_MUTATION = gql`
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

export async function login(email, password) {
  const { data } = await client.mutate({
    mutation: LOGIN_MUTATION,
    variables: { email, password },
  });

  if (data.authLogin.accessToken) {
    localStorage.setItem('token', data.authLogin.accessToken);
    return data.authLogin.user;
  } else {
    throw new Error('Login failed');
  }
}

export function logout() {
  localStorage.removeItem('token');
}