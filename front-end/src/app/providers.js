'use client';
import { ApolloProvider } from '@apollo/client';
import { createApolloClient } from '../../lib/apollo-client';

export function Providers({ children }) {
  const client = createApolloClient();

  return (
    <ApolloProvider client={client}>
      {children}
    </ApolloProvider>
  );
}