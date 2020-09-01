export const state = () => ({
  currentMonthDocumentCount: null,
  lastMonthDocumentCount: null,
  currentMonthSignatureCount: null,
  lastMonthSignatureCount: null,
  loading: null,

});

export const mutations = {
  setCurrentMonthDocumentCount(state, data) {
    state.currentMonthDocumentCount = data.current_month_document_count;
  },
  setLastMonthDocumentCount(state, data) {
    state.lastMonthDocumentCount = data.last_month_document_count;
  },
  setCurrentMonthSignatureCount(state, data) {
    state.currentMonthSignatureCount = data.current_month_signature_count;
  },
  setLastMonthSignatureCount(state, data) {
    state.lastMonthSignatureCount = data.last_month_signature_count;
  },
  toggleLoading(state, value) {
    state.loading = value
  },
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
    console.log(res)
    if (res.status === 200) {
      commit("setCurrentMonthDocumentCount", res.data);
      commit("setLastMonthDocumentCount", res.data);
      commit("setCurrentMonthSignatureCount", res.data);
      commit("setLastMonthSignatureCount", res.data);
      commit("toggleLoading", false);
    }
  },
};

