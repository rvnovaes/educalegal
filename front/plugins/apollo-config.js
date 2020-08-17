import Cookies from 'js-cookie'

export default (context) => {
  return {
    httpEndpoint: 'http://localhost:8001/graphql',
    httpLinkOptions: {
      credentials: 'same-origin',
      // credentials: 'include',
    },
    // authenticationType: 'JWT',

    /*
     * For permanent authentication provide `getAuth` function.
     * The string returned will be used in all requests as authorization header
     */
    getAuth: () =>  'JWT ' + Cookies.get('apollo-token')
    // getAuth: () =>  'Bearer Schrubbles'
  }
}
