const pkg = require('./package')
console.log('ENV', process.env.NODE_ENV)

module.exports = {
  mode: 'universal',
  router: {
    base: '/',
    linkExactActiveClass: 'active',
    // Força autenticacao para acessar as paginas
    // middleware: ['auth'],
    middleware: [],
  },
  /*
  ** Headers of the page
  */
  head: {
    title: 'Educa Legal',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Educa Legal - Advocacia Virtual para Escolas' }
    ],
    link: [
      { rel: 'icon', type: 'image/png', href: 'favicon.png' },
      { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700'},
      { rel: 'stylesheet', href: 'https://use.fontawesome.com/releases/v5.6.3/css/all.css', integrity: "sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/", crossorigin: "anonymous"}
    ]
  },

  /*
  ** Customize the progress-bar color
  */
  loading: { color: '#fff' },

  /*
  ** Global CSS
  */
  css: [
    'assets/css/nucleo/css/nucleo.css',
    'assets/sass/argon.scss'
  ],

  /*
  ** Plugins to load before mounting the App
  */
  plugins: [
    '~/plugins/dashboard/dashboard-plugin',
    '~/plugins/axios-educa-legal',
    {src: '~/plugins/dashboard/full-calendar', ssr: false },
    {src: '~/plugins/dashboard/world-map', ssr: false },
  ],

  /*
  ** Nuxt.js modules
  */
  modules: [
    // Doc: https://axios.nuxtjs.org/usage
    '@nuxtjs/axios',
    '@nuxtjs/pwa',
    // '@nuxtjs/auth',
    '@nuxtjs/toast',
    '@nuxtjs/apollo'
  ],
  /*
  ** Axios module configuration
  */
  axios: {
    // See https://github.com/nuxt-community/axios-module#options
    // Default: http://[HOST]:[PORT][PREFIX]
    // Defines the base URL which is used and prepended to make server side requests.
    // Environment variable API_URL can be used to override baseURL.
    // baseURL: 'http://localhost:8008'
    baseURL: 'http://localhost:8001'
  },

  toast: {
    position: 'top-center',
    iconPack: 'fontawesome',
    duration: 3000,
    register: [
      {
        name: 'defaultSuccess',
        message: (payload) =>
          !payload.msg ? 'Operação bem sucedida' : payload.msg,
        options: {
          type: 'success',
          icon: 'check',
          theme: 'outline'
        }
      },
      {
        name: 'defaultError',
        message: (payload) =>
          !payload.msg ? 'Oops.. Erro inesperado' : payload.msg,
        options: {
          type: 'error',
          icon: 'times',
          theme: 'outline'
        }
      }
    ]
  },
  // auth: {
  //   strategies: {
  //     local: {
  //       endpoints: {
  //         login: { url: '/v2/token/', method: 'post', propertyName: 'access', altProperty: 'refresh' },
  //         logout: false,
  //         user: { url: '/v2/user/', method: 'get', propertyName: false }
  //         // user: false
  //       }
  //     }
  //   },
  //   redirect: {
  //     login: '/',
  //     logout: '/',
  //     home: '/painel'
  //   },
  // },
  // Give apollo module options
  apollo: {
    clientConfigs: {
      default: {
        // httpEndpoint: 'http://localhost:8008/graphql',
        httpEndpoint: 'http://localhost:8001/graphql',
      }
    },
  },
  /*
  ** Build configuration
  */
  build: {
    transpile: [
      'vee-validate/dist/rules'
    ],
    /*
    ** You can extend webpack config here
    */
    extend(config, ctx) {
      // Added Line
      config.devtool = ctx.isClient ? 'eval-source-map' : 'inline-source-map'

      // Run ESLint on save
      // if (ctx.isDev && ctx.isClient) {
      //   config.module.rules.push({
      //     enforce: 'pre',
      //     test: /\.(js|vue)$/,
      //     loader: 'eslint-loader',
      //     exclude: /(node_modules)/
      //   })
      // }

    },
    extractCSS: process.env.NODE_ENV === 'production',
    babel: {
      plugins: [
        [
          "component",
          {
            "libraryName": "element-ui",
            "styleLibraryName": "theme-chalk"
          }
        ]
      ]
    }
  }
}
