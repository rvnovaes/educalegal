import createPersistedState from 'vuex-persistedstate'
// https://github.com/robinvdvleuten/vuex-persistedstate
// paths define os caminhos do store que voce quer persistir. Eg: se eu quisesse persistir somente as escolas
// o paths ficaria paths: ["schools"], etc. Para verificar quais caminhos o persisted state esta mapeando,
// deve ser acessado no navegador Application/Local Storage e deve ser procurada a chave "key" abaixo
export default ({store}) => {
  createPersistedState({
    key: 'educa_legal_vuex',
    paths: ["schools"]
  })(store)
}
