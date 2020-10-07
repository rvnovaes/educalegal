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
  deleteSchool(state, school) {
    const i = state.schools.map(school => school.id).indexOf(school.id);
    state.schools.splice(i, 1);
  },
  addWitness(state, payload) {
      // procura para verificar se ha testemunha vazia
      const w = state.schools.find(s => s.id === Number(payload.schoolId)).witnesses.find(w => w.id === Number(payload.newWitness.id))
      // se nao houver, adiciona testemunha vazia no store
      if (w === undefined){
        state.schools.find(s => s.id === Number(payload.schoolId)).witnesses.push(payload.newWitness)
      }
  },
  updateWitnessId(state, { witness, newId }){
    state.schools.find(s => s.id === Number(witness.school)).witnesses.find(w => w.id === Number(witness.id)).id = newId
  },
  deleteWitness(state, witness) {
    const i = state.schools.find(s => s.id === witness.school).witnesses.map(w => w).indexOf(witness.id)
    state.schools.find(s => s.id === witness.school).witnesses.splice(i, 1);
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
  },
  updateWitnessName(state, payload) {
      state.schools.find(s => s.id === Number(payload.schoolId)).witnesses.find(witness => witness.id === Number(payload.witnessId)).name = payload.name;
  },
  updateWitnessEmail(state, payload) {
    state.schools.find(s => s.id === Number(payload.schoolId)).witnesses.find(witness => witness.id === Number(payload.witnessId)).email = payload.email;
  },
  updateWitnessCPF(state, payload) {
      state.schools.find(s => s.id === Number(payload.schoolId)).witnesses.find(witness => witness.id === Number(payload.witnessId)).cpf = payload.cpf;
  },
  resetState(state) {
    Object.assign(state, getDefaultState());
  },
};

export const getters = {
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getSchool: (state) => (id) => {
    let school = state.schools.find(school => school.id === Number(id));
    // console.log("VUEX: ")
    // console.log(school)
    if (school.id === 0) {
      delete school.id;
    }
    return school;
  },
  getWitnesses: (state) => (id) => {
    return state.schools.find(school => school.id === Number(id)).witnesses;
  },
  getWitness: (state) => (schoolId, witnessId) => {
    return state.schools.find(school => school.id === Number(schoolId)).witnesses.find(witness => witness.id === Number(witnessId));
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
  async createSchool({commit}, school) {
    // Quando EscolaForm esta na operacao de criar, ele adiciona uma escola vazia, com id 0 que recebeu de escolas / index
    // Essa escola provisoria deve ser removida da lista de escolas do vuex
    commit("deleteSchool", school);
    // Depois de removida a escola, sera feito a criaca da escola no back
    // O botao que salva a nova escola e chama essa action redireciona depois para a lista de escolas
    // que recarrega todas as escolas de novo do banco, incluindo a recem criada
    await this.$axios.post(`/v2/schools/`, school);
  },
  async updateWitness({commit, getters, state}, witness){
    // pega a testemunha do vuex
    const w = getters.getWitness(witness.school, witness.id)
    const payload = {
      id: w.id,
      name: w.name,
      email: w.email,
      cpf: w.cpf,
      school: w.school,
      tenant: w.tenant
    }
    // retorna a resposta para a tela que fará a exibicao dos erros
    return  await this.$axios.patch(`v2/schools/${witness.school}/witnesses/${witness.id}`, payload)
  },
  async createWitness({commit, getters}, witness) {
    // Pega a testemunha do vuex
    const w = getters.getWitness(witness.school, witness.id)
    // Monta o payload com os dados da testemunha que ja estao no vuex.
    // Entretanto, como a testemunha recem criada tem id = 0, nao passa id no payload
    const payload = {
      name: w.name,
      email: w.email,
      cpf: w.cpf,
      school: w.school,
      tenant: w.tenant
    };
    const res = await this.$axios.post(`v2/schools/${witness.school}/witnesses`, payload)
    if (res.status === 201) {
      // pega a id retornada do backend
      const newId = res.data.id
      // Atualiza a testemunha do vuex que antes tinha id = 0 com a id retornada pelo backend
      commit("updateWitnessId", { witness, newId } )
    } else {
      commit("deleteWitness", w)
    }
    return res
  },
  async deleteWitness({commit}, witness) {
    const res = await this.$axios.delete(`/v2/schools/${witness.school}/witnesses/${witness.id}`);
    if (res.status === 204) {
      commit("deleteWitness", witness);
    }
    return res;
  },
  resetState({commit}) {
    commit("resetState");
  }
};
