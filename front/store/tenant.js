// https://tahazsh.com/vuebyte-reset-module-state
const getDefaultState = () => {
  return {
    tenantName: null,
    planName: null,
    planValue: null,
    planDocumentLimit: null,
    planUseGed: null,
    planUseBulkInterview: null,
    planUseEsignature: null,
    tenantGedData: null,
    loading: null,
  }
}

// Entretanto, tivemos que repetir o estado na const state, pq que se chamassemos a funcao:
// export const state = getDefaultState();
// o vue ficava dando um warning de que state deve retornar um objeto
export const state = () => ({
  tenantName: null,
  planName: null,
  planValue: null,
  planDocumentLimit: null,
  planUseGed: null,
  planUseBulkInterview: null,
  planUseEsignature: null,
  tenantGedData: null,
  loading: null,
});

export const mutations = {
  setTenantData(state, tenantData) {
    state.tenantName = tenantData.name;
  },
  setPlanName(state, tenantData) {
    state.planName = tenantData.plan.name;
  },
  setPlanValue(state, tenantData) {
    state.planValue = tenantData.plan.value;
  },
  setPlanDocumentLimit(state, tenantData) {
    state.planDocumentLimit = tenantData.plan.document_limit;
  },
  setPlanUseGed(state, tenantData){
    state.planUseGed = tenantData.plan.use_ged;
  },
  setPlanUseBulk(state, tenantData){
    state.planUseBulkInterview = tenantData.plan.use_bulk_interview;
  },
  setPlanUseEsignature(state, tenantData){
    state.planUseEsignature = tenantData.plan.use_esignature;
  },
  setTenantGedData(state, gedData) {
    state.tenantGedData = gedData;
  },
  toggleLoading(state, value) {
    state.loading = value
  },
  resetState (state) {
    Object.assign(state, getDefaultState())
  }
};

export const actions = {
  async fetchTenantData({commit}, tenantID) {
    commit("toggleLoading", true);
    const res = await this.$axios.get("/v2/tenants/" + tenantID);
    if (res.status === 200) {
      commit("setTenantData", res.data);
      commit("setPlanName", res.data);
      commit("setPlanValue", res.data);
      commit("setPlanDocumentLimit", res.data);
      commit("setPlanUseGed", res.data);
      commit("setPlanUseBulk", res.data);
      commit("setPlanUseEsignature", res.data);
      commit("toggleLoading", false);
    }
  },
  async fetchTenantGedData({commit}, tenantID) {
    commit("toggleLoading", true);
    const res = await this.$axios.get("/v2/tenants/" + tenantID + "/ged_data");
    if (res.status === 200) {
      commit("setTenantGedData", res.data);
      commit("toggleLoading", false);
    }
  },
  resetState({commit}){
    commit("resetState")
  }
};
