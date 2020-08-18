export const state = () => ({
  schools: [],
  currentSchool: null
})

export const mutations = {
  setSchool (state, school) {
    state.currentSchool = school
  },
  addSchool (state, school) {
    state.schools.push(school)
  },
  setSchools (state, schools){
    state.schools = schools
  }
}

export const getters = {
  getAllSchools(state){
    return state.schools
  },
  // https://vuex.vuejs.org/guide/getters.html#method-style-access
  getSchool:(state) => (id) => {
    return state.schools.find(school => school.id === Number(id))
  }
}

export const actions = {
  fetchAllSchools({commit}) {
    return this.$axios.get('http://localhost:8001/v2/tenant/schools').then(res => {
      if (res.status === 200) {
        commit('setSchools', res.data.results)
      }
    })
  },
  fetchSchool({commit}, id) {
    return this.$axios.get(`http://localhost:8001/v2/tenant/schools/${id}`).then(res => {
      if (res.status === 200) {
        commit('setSchool', res.data)
      }
    })
  },
  // fetchSchool({commit}, id) {
  //   return this.$axios.get(`http://localhost:8001/v2/tenant/schools/${id}`).then(res => {
  //     if (res.status === 200) {
  //       commit('setSchool', res.data)
  //     }
  //   })
  // },
}
