export const state = () => ({
  schools: [],
});

export const mutations = {
  addSchool(state, school) {
    state.schools.push(school);
  },
  setSchools(state, schools) {
    state.schools = schools;
  },
  deleteSchool(state, school) {
    const i = state.schools.map(school => school.id).indexOf(school.id);
    state.schools.splice(i, 1);
  },
  updateName(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).name = payload.name;
  },
  updateLegalName(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).legal_name = payload.legal_name;
  },
  updateCNPJ(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).cnpj = payload.cnpj;
  },
  updateLegalNature(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).legal_nature = payload.legal_nature;
  },
  updateCity(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).city = payload.city;
  },
  updateUF(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).state = payload.state;
  }
};

export const getters = {
  getAllSchools(state) {
    return state.schools;
  },
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getSchool: (state) => (id) => {
    return state.schools.find(school => school.id === Number(id));
  }
};

export const actions = {
  fetchAllSchools({commit}) {
    return this.$axios.get("/v2/tenant/schools").then(res => {
      if (res.status === 200) {
        commit("setSchools", res.data.results);
      }
    });
  },
  deleteSchool({commit}, school) {
    return this.$axios.delete(`/v2/tenant/schools/${school.id}`).then(res => {
      if (res.status === 200) {
        console.log(res);
        commit("deleteSchool", school);
      }
    });
  },
  createSchool({commit}, school) {
    return this.$axios.post(`/v2/tenant/schools/`, school).then(res => {
      if (res.status === 200) {
        console.log(res);
        commit("addSchool", school);
      }
    });
  }

  // fetchSchool({commit}, id) {
  //   return this.$axios.get(`http://localhost:8001/v2/tenant/schools/${id}`).then(res => {
  //     if (res.status === 200) {
  //       commit('setSchool', res.data)
  //     }
  //   })
  // },
};
