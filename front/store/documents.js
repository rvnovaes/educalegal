export const state = () => ({
  documents: [],
  count: 0,
  loading: true

});

export const mutations = {
  addDocument(state, document) {
    state.schools.push(document);
  },
  setDocuments(state, documents) {
    state.documents = [...state.documents, ...documents]
  },
  setDocumentCount(state, count) {
    state.count = count;
  },
  cleanDocuments(state) {
    state.documents = [];
    state.count = 0
  },
  loadingFalse(state) {
    state.loading = false;
  },
  loadingTrue(state) {
    state.loading = true;
  }
};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getDocument: (state) => (id) => {
    return state.documents.find(document => document.id === Number(id));
  },
  getLoadedDocumentsListCount: (state) => {
    return state.documents.length;
  },
  getTotalDocumentsCount: (state) => {
    return state.count;
  }
};

export const actions = {
  // async fetchAllDocuments({commit}) {
  //   const res = await this.$axios.get("/v2/documents");
  //   if (res.status === 200) {
  //     commit("setDocuments", res.data);
  //   }
  // },
  async fetchPaginatedDocuments({commit}, payload) {
    commit("loadingTrue");
    const res = await this.$axios.get("/v2/documents/", {
      params:
        {
          limit: 50,
          offset: payload.offset,
          status: payload.status,
          school: payload.school
        }
    });
    // console.log(res);
    // console.log(res.data.count);
    // console.log(res.data.results);
    if (res.status === 200) {
      commit("setDocuments", res.data.results);
      commit("setDocumentCount", res.data.count);
      commit("loadingFalse");
    }
  },
  deleteDocument({commit}) {
    console.log("Delete document action");
  }
};

