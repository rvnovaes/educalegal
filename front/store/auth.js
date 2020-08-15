// https://blog.logrocket.com/handling-authentication-in-your-graphql-powered-vue-app/
// https://stackoverflow.com/questions/57666738/vuex-classic-mode-for-store-is-deprecated-and-will-be-removed-in-nuxt-3

import tokenAuth from "@/queries/tokenAuth";


export const state = () => ({
      token: null,
      user: {},
      authStatus: false
    })

export const getters = {
      isAuthenticated: state => !!state.token,
      authStatus: state => state.authStatus,
      user: state => state.user
    }

export const mutations = {
      set_token (state, token) {
        state.token = token
      },
      login_user (state, user) {
        state.authStatus = true
        state.user = { ...user }
      },
      logout_user (state) {
        state.authStatus = ''
        state.token = '' && localStorage.removeItem('apollo-token')
      }
    }
export const actions = {
      // async register ({ commit, dispatch }, authDetails) {
      //   try {
      //     const { data } = await apolloClient.mutate({ mutation: REGISTER_USER, variables: { ...authDetails } })
      //     const token = JSON.stringify(data.createUser.token)
      //     commit('SET_TOKEN', token)
      //     localStorage.setItem('apollo-token', token)
      //     dispatch('setUser')
      //   } catch (e) {
      //     console.log(e)
      //   }
      // },
      async login({commit, dispatch}, credentials) {
        let client = this.app.apolloProvider.defaultClient
        try {
          const res = await client.mutate({
            mutation: tokenAuth,
            variables: {
              username: credentials.username,
              password: credentials.password
            }
          }).then(data => console.log(data))
          await client.$apolloHelpers.onLogin(res.token)

          // const token = JSON.stringify(authData.login.token)
          // commit('set_token', token)
          // localStorage.setItem('apollo-token', token)
          // dispatch('setUser')
        } catch (e) {
          console.log(e)
        }
      }
      //   async setUser ({ commit }) {
      //     const { data } = await apolloClient.query({ query: LOGGED_IN_USER })
      //     commit('LOGIN_USER', data.me)
      //   },
      //   async logOut ({ commit, dispatch }) {
      //     commit('LOGOUT_USER')
      //   }
      // }
  }

