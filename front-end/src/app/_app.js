import { ApolloProvider } from '@apollo/client';
import { initializeApollo } from '../../lib/apollo-client';

function MyApp({ Component, pageProps, apolloClient }) {
  return (
    <ApolloProvider client={apolloClient}>
      <Component {...pageProps} />
    </ApolloProvider>
  );
}

MyApp.getInitialProps = async (appContext) => {
  const apolloClient = initializeApollo();

  // Run getInitialProps of the page being rendered
  const appProps = await App.getInitialProps(appContext);

  return {
    ...appProps,
    apolloClient,
  };
};

export default MyApp;