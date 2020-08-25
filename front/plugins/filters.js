import Vue from 'vue'

// https://github.com/nuxt/nuxt.js/issues/231 -> How to create filters for the entire application
Vue.filter("capitalize", function (value) {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
  })
