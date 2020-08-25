import moment from 'moment';

export const state = () => ({
  interviews: [],
});

export const mutations = {
  appendDocuments(state, interviews) {
    state.interviews = [...state.interviews, ...interviews];
  },

};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getInterview: (state) => (id) => {
    return state.interviews.find(interviews => interviews.id === Number(id));
  },
};

export const actions = {
  async fetchPaginatedDocuments({commit}, payload) {
    const res = await this.$axios.get("/v2/documents/", {
      params:
        {
          limit: 50,
          offset: payload.offset,
          status: payload.statusFilter,
          school: payload.schoolFilter,
          orderByCreatedDate: payload.orderByCreatedDate,
          createdDateRange: payload.createdDateRange
        }
    });
    // console.log("Depois da requisicao")
    // console.log(res.data.results)
    let documents = res.data.results
    documents.forEach(function(doc, index) {
      this[index].created_date = moment(doc.created_date).format('DD/MM/YYYY')
      this[index].altered_date = moment(doc.altered_date).format('DD/MM/YYYY')
    }, documents); // use arr as this
    // console.log(documents)
    if (res.status === 200) {
      commit("appendDocuments", documents);
      commit("setDocumentCount", res.data.count);
      commit("loadingFalse");
    }
  },
};

