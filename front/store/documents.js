export const state = () => ({
  documents: [],
  count: 0,

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
  }
};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getDocument: (state) => (id) => {
    return state.documents.find(document => document.id === Number(id));
  },
  getLoadedDocumentsListCount: (state) => {
    return state.documents.length;
  }
};

export const actions = {
  // async fetchAllDocuments({commit}) {
  //   const res = await this.$axios.get("/v2/documents");
  //   if (res.status === 200) {
  //     commit("setDocuments", res.data);
  //   }
  // },
  async fetchPaginatedDocuments({commit}, offset) {
    const res = await this.$axios.get("/v2/documents/", {
      params:
        {
          limit: 50,
          offset: offset
        }
    });
    // console.log(res);
    // console.log(res.data.count);
    // console.log(res.data.results);
    if (res.status === 200) {
      commit("setDocuments", res.data.results);
      commit("setDocumentCount", res.data.count);
    }
  },
  deleteDocument({commit}) {
    console.log("Delete document action");
  }
};

