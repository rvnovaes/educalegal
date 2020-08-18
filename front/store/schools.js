export const state = () => ({
  schools: [],
  currentSchool: null
})

export const mutations = {
  setSchool (state, school) {
    state.schools = school
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
  getCurrentSchool(state){
    return state.currentSchool
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
}
