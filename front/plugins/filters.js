import Vue from 'vue'
import moment from 'moment'

// https://github.com/nuxt/nuxt.js/issues/231 -> How to create filters for the entire application
Vue.filter("capitalize", function (value) {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
  })

Vue.filter('formatDateTime', function(value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY hh:mm:ss')
  }
})
