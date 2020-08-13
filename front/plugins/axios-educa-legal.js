export default function ({$axios}){

  // $axios.setToken('Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTk3MzUwMzk3LCJqdGkiOiI3ZWRhMzFjMzY0Y2E0M2UxYWFlYTZkNTRlNDAwYTEyMSIsInVzZXJfaWQiOjgxfQ.B8TJTRWbqD5TM4mi7r6G9ons4_xh-Ox08SVTm34u5-o', 'Bearer');

  $axios.onRequest(config => {
    console.log('Making request to ' + config.url)
    }
  )
}
