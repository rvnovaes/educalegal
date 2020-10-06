const pkg = require("./package");
const NODE_ENV = process.env.NODE_ENV;
console.log(NODE_ENV)

module.exports = {
  router: {
    base: "/",
    linkExactActiveClass: "active",
    // Força autenticacao para acessar as paginas
    middleware: ["auth"],
  },
  /*
  ** Headers of the page
  */
  head: {
    title: "Educa Legal",
    meta: [
      {charset: "utf-8"},
      {name: "viewport", content: "width=device-width, initial-scale=1"},
      {hid: "description", name: "description", content: "Educa Legal - Advocacia Virtual para Escolas"}
    ],
    link: [
      {rel: "icon", type: "image/x-icon", href: "favicon.ico"},
      {rel: "stylesheet", href: "https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700"},
      {
        rel: "stylesheet",
        href: "https://use.fontawesome.com/releases/v5.6.3/css/all.css",
        integrity: "sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/",
        crossorigin: "anonymous"
      }
    ]
  },

  /*
  ** Customize the progress-bar color
  */
  loading: {color: "#fff"},

  /*
  ** Global CSS
  */
  css: [
    "assets/css/nucleo/css/nucleo.css",
    "assets/sass/argon.scss"
  ],

  /*
  ** Plugins to load before mounting the App
  */
  plugins: [
    "~/plugins/dashboard/dashboard-plugin",
    "~/plugins/axios-educa-legal",
    "~/plugins/filters",
    {src: "~/plugins/dashboard/full-calendar", ssr: false},
    {src: "~/plugins/dashboard/world-map", ssr: false},
  ],

  /*
  ** Nuxt.js modules
  */
  modules: [
    // Doc: https://axios.nuxtjs.org/usage
    "@nuxtjs/axios",
    "@nuxtjs/pwa",
    "@nuxtjs/auth",
  ],

  /*
  ** Axios module configuration
  */
  axios: {
    // See https://github.com/nuxt-community/axios-module#options
    // Default: http://[HOST]:[PORT][PREFIX]
    // Defines the base URL which is used and prepended to make server side requests.
    // Environment variable API_URL can be used to override baseURL.
    // baseURL: 'http://educalegal:8008'
    baseURL: process.env.BACKEND_URL
  },

  server: {
    port: 3000, // default: 3000
    host: "0.0.0.0" // default: localhost
  },

  toast: {
    position: "top-center",
    iconPack: "fontawesome",
    duration: 3000,
    register: [
      {
        name: "defaultSuccess",
        message: (payload) =>
          !payload.msg ? "Operação bem sucedida" : payload.msg,
        options: {
          type: "success",
          icon: "check",
          theme: "outline"
        }
      },
      {
        name: "defaultError",
        message: (payload) =>
          !payload.msg ? "Oops.. Erro inesperado" : payload.msg,
        options: {
          type: "error",
          icon: "times",
          theme: "outline"
        }
      }
    ]
  },
  auth: {
    strategies: {
      // getTenantScheme: {
      //   _scheme: '~/schemes/CustomScheme',
      //   endpoints: {
      //     login: { url: '/v2/token/', method: 'post', propertyName: 'access', altProperty: 'refresh' },
      //     user: { url: '/v2/user/', method: 'get', propertyName: false },
      //     logout: false,
      //   }

      local: {
        endpoints: {
          login: {url: "/v2/token/", method: "post", propertyName: "access", altProperty: "refresh"},
          user: {url: "/v2/users/", method: "get", propertyName: false},
          logout: false,
        }
      }
    },
    redirect: {
      login: "/",
      logout: "/",
      home: "/painel"
    },
  },
  build: {
    transpile: [
      "@nuxtjs/auth",
      "vee-validate/dist/rules"
    ],
    /*
    ** You can extend webpack config here
    */
    extend(config, ctx) {
      // Added Line
      config.devtool = ctx.isClient ? "eval-source-map" : "inline-source-map";

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
    extractCSS: process.env.NODE_ENV === "production",
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
};
