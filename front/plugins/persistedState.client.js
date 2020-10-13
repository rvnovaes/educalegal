import createPersistedState from 'vuex-persistedstate'
// https://github.com/robinvdvleuten/vuex-persistedstate
// paths define os caminhos da aplicacao que voce quer persistir. Eg: se eu quisesse persistir somente as escolas
// o paths ficaria paths: ["escolas"], etc.
export default ({store}) => {
  createPersistedState({
    key: 'educa_legal_vuex',
    // paths: ["escolas"]
  })(store)
}
