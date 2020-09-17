import Swal from "sweetalert2";

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
  },
};

export const actions = {
  async fetchAllSchools({commit}) {
    const res = await this.$axios.get("/v2/schools");
    if (res.status === 200) {
      const schools = res.data.results
      commit("setSchools", schools);
      if (schools.length === 0) {
        await Swal.fire({
          title: "Bem-vindo ao Educa Legal!",
          text: "Para começar a usar a plataforma, você deve cadastrar sua primeira escola. Os dados da escola cadastrada serão usados na geração dos contratos e documentos.",
          icon: "success",
          customClass: {
            confirmButton: "btn btn-success btn-fill",
          },
          confirmButtonText: "Entendido. Leve-me leve até lá!",
          buttonsStyling: false
        });
        await this.$router.push({path: "/escolas/criar"});
      }
    }
  },
  async deleteSchool({commit}, school) {
    const res = await this.$axios.delete(`/v2/schools/${school.id}`);
    if (res.status === 204) {
      commit("deleteSchool", school);
    }
    return res
  },
  async createSchool({commit}, school) {
    const res = await this.$axios.post(`/v2/schools/`, school);
    if (res.status === 200) {
      console.log(res);
      commit("addSchool", school);
    }
  }
};
