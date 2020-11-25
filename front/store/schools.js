import Swal from "sweetalert2";

// https://tahazsh.com/vuebyte-reset-module-state
const getDefaultState = () => {
  return {
    schools: []
  };
};

// Entretanto, tivemos que repetir o estado na const state, pq que se chamassemos a funcao:
// export const state = getDefaultState();
// o vue ficava dando um warning de que state deve retornar um objeto

export const state = () => ({
  schools: [],
});

export const mutations = {
  addSchool(state, school) {
    state.schools.push(school);
  },
  addSchools(state, schools) {
    // itera sobre um array de escolas. Se o id da escola for encontrado no state.schools, ignora.
    // se nao for encontrado, adiciona a escola ao array
    // se isso nao for feito, na action fetchAllSchools, que invoca essa mutation, a lista de escolas
    // vai sendo acrescida de elementos repetidos que aparecerao, por isso mesmo, repetidos na listagem
    schools.forEach(function (item, index) {
      let currentSchool = state.schools.find(school => school.id === item.id);
      if (currentSchool == null) {
        state.schools.push(item);
      }
    });
  },
  updateSchoolId(state, {school, newId}) {
    state.schools.find(s => s.id === Number(school.id)).id = newId;
  },
  deleteSchool(state, school) {
    console.log("deleteSchool");
    console.log(JSON.stringify(school));
    const i = state.schools.map(school => school.id).indexOf(school.id);
    state.schools.splice(i, 1);
  },
  addRepresentative(state, payload) {
    // procura para verificar se ha representante vazio
    const w = state.schools.find(s => s.id === Number(payload.schoolId)).representatives.find(w => w.id === Number(payload.newRepresentative.id));
    // se nao houver, adiciona representante vazio no store
    if (w === undefined) {
      state.schools.find(s => s.id === Number(payload.schoolId)).representatives.push(payload.newRepresentative);
    }
  },
  updateRepresentativeId(state, {representative, newId}) {
    state.schools.find(w => w.id === Number(representative.school)).representatives.find(w => w.id === Number(representative.id)).id = newId;
  },
  deleteRepresentative(state, payload) {
    const i = state.schools.find(s => s.id === payload.school).representatives.map(w => w).indexOf(payload.id);
    state.schools.find(s => s.id === payload.school).representatives.splice(i, 1);
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
  },
  updateRepresentativeName(state, payload) {
    state.schools.find(s => s.id === Number(payload.schoolId)).representatives.find(representative => representative.id === Number(payload.representativeId)).name = payload.name;
  },
  updateRepresentativeEmail(state, payload) {
    state.schools.find(s => s.id === Number(payload.schoolId)).representatives.find(representative => representative.id === Number(payload.representativeId)).email = payload.email;
  },
  updateRepresentativeCPF(state, payload) {
    state.schools.find(s => s.id === Number(payload.schoolId)).representatives.find(representative => representative.id === Number(payload.representativeId)).cpf = payload.cpf;
  },
  resetState(state) {
    Object.assign(state, getDefaultState());
  },
};

// https://vuex.vuejs.org/guide/getters.html#method-style-access
export const getters = {
  getSchool: (state) => (id) => {
    return state.schools.find(school => school.id === Number(id));
  },
  getRepresentatives: (state) => (id) => {
    return state.schools.find(school => school.id === Number(id)).representatives;
  },
  getRepresentative: (state) => (schoolId, representativeId) => {
    return state.schools.find(school => school.id === Number(schoolId)).representatives.find(representative => representative.id === Number(representativeId));
  },
};

export const actions = {
  async fetchAllSchools({commit}) {
    const res = await this.$axios.get("/v2/schools");
    if (res.status === 200) {
      const schools = res.data.results;
      commit("addSchools", schools);
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
    return res;
  },
  async createSchool({commit, getters}, school) {
    // Quando EscolaForm esta na operacao de criar, ele adiciona uma escola vazia, com id 0 que recebeu de escolas / index
    // Pegamos essa escola vazia do vuex, fazemos uma copia para criar a payload. Em js variaveis que apontam para objetos sao ponteiros.
    // Para fazer uma copia completa dos valores (deep copy) de modo que a referencia seja quebrada, e preciso usar JSON.stringify
    let payload = JSON.parse(JSON.stringify(getters.getSchool(school.id)));
    // remove a id do objeto
    if (payload["id"] === 0) {
      delete payload["id"];
    }
    const res = await this.$axios.post(`/v2/schools/`, payload);
    if (res.status === 201) {
      const newId = res.data.id;
      commit("updateSchoolId", {school, newId});
    } else {
      commit("deleteSchool", school);
    }
    return res;
  },
  async updateSchool({commit, getters, state}, school) {
    // pega a representante do vuex
    const payload = JSON.parse(JSON.stringify(getters.getSchool(school.id)));
    // retorna a resposta para a tela que fará a exibicao dos erros
    return await this.$axios.patch(`v2/schools/${school.id}`, payload);
  },
  async updateRepresentative({commit, getters, state}, representative) {
    // pega a representante do vuex
    const payload = JSON.parse(JSON.stringify(getters.getRepresentative(representative.school, representative.id)));
    // retorna a resposta para a tela que fará a exibicao dos erros
    return await this.$axios.patch(`v2/schools/${representative.school}/representatives/${representative.id}`, payload);
  },
  async createRepresentative({commit, getters}, representative) {
    // Pega a representante do vuex
    let payload = JSON.parse(JSON.stringify(getters.getRepresentative(representative.school, representative.id)));
    // Monta o payload com os dados do representante que ja estao no vuex.
    // Entretanto, como o representante recem criado tem id = 0, nao passa id no payload
    if (payload["id"] === 0) {
      delete payload["id"];
    }
    const res = await this.$axios.post(`v2/schools/${representative.school}/representatives`, payload);
    if (res.status === 201) {
      // pega a id retornada do backend
      const newId = res.data.id;
      // Atualiza o representante do vuex que antes tinha id = 0 com a id retornada pelo backend
      commit("updateRepresentativeId", {representative, newId});
    } else {
      commit("deleteRepresentative", representative);
    }
    return res;
  },
  async deleteRepresentative({commit}, representative) {
    const res = await this.$axios.delete(`/v2/schools/${representative.school}/representatives/${representative.id}`);
    if (res.status === 204) {
      commit("deleteRepresentative", representative);
    }
    return res;
  },
  resetState({commit}) {
    commit("resetState");
  }
};
