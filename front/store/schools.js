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
  updateSite(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).site = payload.site;
  },
  updateEmail(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).email = payload.email;
  },
  updateZip(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).zip = payload.zip;
  },
  updateStreet(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).street = payload.street;
  },
  updateStreetNumber(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).street_number = payload.street_number;
  },
  updateUnit(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).unit = payload.unit;
  },
  updateNeighborhood(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).neighborhood = payload.neighborhood;
  },
  updatePhone(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).phone = payload.phone;
  },
  updateCity(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).city = payload.city;
  },
  updateUF(state, payload) {
    state.schools.find(school => school.id === Number(payload.id)).state = payload.state;
  }
};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getSchool: (state) => (id) => {
    return state.schools.find(school => school.id === Number(id));
  }
};

export const actions = {
  async fetchAllSchools({commit}) {
    const res = await this.$axios.get("/v2/tenant/schools");
    if (res.status === 200) {
      commit("setSchools", res.data.results);
    }
  },
  async deleteSchool({commit}, school) {
    const res = await this.$axios.delete(`/v2/tenant/schools/${school.id}`);
    if (res.status === 204) {
      console.log(res);
      commit("deleteSchool", school);
    }
  },
  async createSchool({commit}, school) {
    const res = await this.$axios.post(`/v2/tenant/schools/`, school);
    if (res.status === 200) {
      console.log(res);
      commit("addSchool", school);
    }
  }

  // fetchSchool({commit}, id) {
  //   return this.$axios.get(`http://localhost:8001/v2/tenant/schools/${id}`).then(res => {
  //     if (res.status === 200) {
  //       commit('setSchool', res.data)
  //     }
  //   })
  // },
};
