// export default function ({ $http }) {
//   $http.onRequest(config => {
//     console.log('Making request to ' + config.url)
//     // const token = this.$store.state.token
//     // options.header.set('Authorization', `JWT ${token}`)
//   })
//
//   // $http.onRetry(async (request, options, errors, retryCount) => {
//   //   const token = await ky('https://example.com/refresh-token')
//   //   options.header.set('Authorization', `Bearer ${token}`)
//   // })
//
//   $http.onError(error => {
//     if (error.statusCode === 500) {
//       alert('Request Error!')
//     }
//     // Tip: error.response will be undefined if the connection dropped to the server
//     // Tip: You can use error.response.data to get response message
//     // Tip: You can return an object or Promise as fallback response to avoid rejection
//   })
// }
