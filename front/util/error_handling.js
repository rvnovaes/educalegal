export function treat_error(error){
  if (error.response) {
    // Request made and server responded
    console.log(error.response.data);
    console.log(error.response.status);
    console.log(error.response.headers);
    return 'Erro: ' + error.response.status + ' - ' + JSON.stringify(error.response.data, null, '\t')
  } else if (error.request) {
    // The request was made but no response was received
    console.log(error.request);
    return error.request
  } else {
    // Something happened in setting up the request that triggered an Error
    console.log('Error', error.message);
    return error.message
  }
}
