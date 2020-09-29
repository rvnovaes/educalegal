// https://tahazsh.com/vuebyte-reset-module-state
const getDefaultState = () => {
  return {
    "totalDocsCount": null,
    "cmDocsCount": null,
    "lmDocsCount": null,
    "cmInProgressDocsCount": null,
    "lmInProgressDocsCount": null,
    "cmSignatureCount": null,
    "lmSignatureCount": null,
    "cmInProgressSignatureCount": null,
    "lmInProgressSignatureCount": null,
    loading: null,
  }
}

// Entretanto, tivemos que repetir o estado na const state, pq que se chamassemos a funcao:
// export const state = getDefaultState();
// o vue ficava dando um warning de que state deve retornar um objeto

export const state = () => ({
  "totalDocsCount": null,
  "cmDocsCount": null,
  "lmDocsCount": null,
  "cmInProgressDocsCount": null,
  "lmInProgressDocsCount": null,
  "cmSignatureCount": null,
  "lmSignatureCount": null,
  "cmInProgressSignatureCount": null,
  "lmInProgressSignatureCount": null,
  loading: null,
});

export const mutations = {
  setDashboardData(state, data) {
    state.totalDocsCount = data.total_docs_count
    state.cmDocsCount = data.cm_docs_count
    state.lmDocsCount = data.lm_docs_count
    state.cmInProgressDocsCount = data.cm_in_progress_docs_count;
    state.lmInProgressDocsCount = data.lm_in_progress_docs_count
    state.cmSignatureCount = data.cm_signature_count
    state.lmSignatureCount = data.lm_signature_count
    state.cmInProgressSignatureCount = data.cm_in_progress_signature_count
    state.lmInProgressSignatureCount = data.lm_in_progress_signature_count
  },
  toggleLoading(state, value) {
    state.loading = value
  },
  resetState (state) {
    Object.assign(state, getDefaultState())
  }
};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getInterview: (state) => (id) => {
    return state.interviews.find(interviews => interviews.id === Number(id));
  },
};

export const actions = {
  async fetchDashBoardData({commit}) {
    commit("toggleLoading", true);
    const res = await this.$axios.get("/v2/dashboard/");
    if (res.status === 200) {
      commit("setDashboardData", res.data);
      commit("toggleLoading", false);
    }
  },
  resetState({commit}){
    commit("resetState")
  }
};

