export const state = () => ({
  interviews: [],
  loading: null,
});

export const mutations = {
  setInterviews(state, interviews) {
    state.interviews = interviews;
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
  async fetchAllInterviews({commit}) {
    commit("toggleLoading", true);
    const res = await this.$axios.get("/v2/interviews/");
    let interviews = res.data.results
    if (res.status === 200) {
      commit("setInterviews", interviews);
      commit("toggleLoading", false);
    }
  },
};

