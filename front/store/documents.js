import moment from 'moment';

const getDefaultState = () => {
  return {
    documents: [],
    createdDateOrdering: null,
    count: 0,
    loading: null,
    statusFilter: [],
    schoolFilter: []
  }
}

export const state = () => ({
  documents: [],
  createdDateOrdering: null,
  count: 0,
  loading: null,
  statusFilter: [],
  schoolFilter: []
});

export const mutations = {
  appendDocuments(state, documents) {
    // console.log("appendDocuments")
    state.documents = [...state.documents, ...documents];
  },
  setDocumentCount(state, count) {
    // console.log("setDocumentCount")
    state.count = count;
  },
  cleanDocuments(state) {
    state.documents = [];
    state.count = 0;
  },
  toggleLoading(state, value) {
    state.loading = value
  },
  resetState (state) {
    Object.assign(state, getDefaultState())
  },
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
  async fetchPaginatedDocuments({commit}, payload) {
    commit("toggleLoading", true);
    // TODO parametro de pegar onlyParents false
    const res = await this.$axios.get("/v2/documents/", {
      params:
        {
          limit: 50,
          offset: payload.offset,
          documentName: payload.documentNameFilter,
          documentPart: payload.documentPartFilter,
          status: payload.statusFilter,
          school: payload.schoolFilter,
          interview: payload.interviewFilter,
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
      commit("toggleLoading", false);
    }
  },
  resetState({commit}){
    commit("resetState")
  }
};


