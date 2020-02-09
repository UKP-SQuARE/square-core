import Vue from 'vue'
import Vuex from 'vuex'

import { fetchResults, loginUser, fetchSkills, updateSkill, deleteSkill, createSkill, fetchSelectors } from '@/api'
//import { isValidJWT } from '@/utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    jwt: "",
    currentResults: [],
    currentQuestion: "There are no bad questions.",
    availableSkills: [],
    mySkills: [],
    availableSkillSelectors: [],
    queryOptions:  {
      selector: "",
      selectedSkills: [],
      maxQuerriedSkills: 3,
      maxResultsPerSkill: 10
    },
    flags: {
      initialisedSelectedSkills: false,
      initialisedSelector: false
    }
  },

  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentResults = payload.results
    },
    initQueryOptions(state) {
      if (!state.flags.initialisedSelectedSkills) {
        state.queryOptions.selectedSkills = state.availableSkills
        state.flags.initialisedSelectedSkills = true
      }
      if (!state.flags.initialisedSelector) {
        state.queryOptions.selector = state.availableSkillSelectors[0]
        state.flags.initialisedSelector = true
      }
    },
    setSkills(state, payload){
      const lenSkills = state.availableSkills.length
      state.availableSkills = payload.skills
      if (state.user){
        state.mySkills = payload.skills.filter(sk => sk.owner_id === state.user.id)
      }
      // Want to reset selected skills if more skills are available (due to login or something like that)
      if (lenSkills < state.availableSkills.length) {
        state.flags.initialisedSelectedSkills = false
      }
    },
    setJWT(state, payload) {
      state.jwt = payload.jwt
      if (payload.jwt && payload.jwt.split('.').length == 3) {
        const data = JSON.parse(atob(payload.jwt.split('.')[1]))
        state.user = data.sub
      }
    },
    setQueryOptions(state, payload) {
      state.queryOptions = payload.queryOptions
    },
    setSelectors(state, payload) {
      state.availableSkillSelectors = payload.selectors
    }
  },

  actions: {
    answerQuestion(context, {question, options}) {
      return fetchResults(question, options)
        .then((response) => {
          context.commit("setAnsweredQuestion", {results: response.data, question: question})
          context.commit("setQueryOptions", {queryOptions: options})
        })
    },
    login(context, {username, password}) {
      return loginUser(username, password)
        .then((response) => {
          context.commit("setJWT", {jwt: response.data.token})
        })
    },
    signout(context) {
      context.commit("setJWT", {jwt: ""})
    },
    updateSkills(context){
      return fetchSkills(context.state.jwt)
        .then((response) => context.commit("setSkills", {skills: response.data}))
    },
    updateSelectors(context){
      return fetchSelectors()
        .then((response) => context.commit("setSelectors", {selectors: response.data}))
    },
    updateSkill(context, {skill}) {
      return updateSkill(skill.id, skill, context.state.jwt)
      .then(() => context.dispatch("updateSkills"))
    },
    createSkill(context, {skill}) {
      return createSkill(skill, context.state.jwt)
      .then(() => context.dispatch("updateSkills"))
    },
    deleteSkill(context, {skillId}) {
      return deleteSkill(skillId, context.state.jwt)
        .then(() => context.dispatch("updateSkills"))
    }
  },

  getters: {
    isAuthenticated: (state) => () => {
      let jwt = state.jwt
      if (!jwt || jwt.split('.').length < 3) {
        return false
      }
      let data = JSON.parse(atob(jwt.split('.')[1]))
      let exp = new Date(data.exp * 1000)
      let now = new Date()
      return now < exp
    }
  }
})
