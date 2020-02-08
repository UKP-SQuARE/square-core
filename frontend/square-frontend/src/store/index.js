import Vue from 'vue'
import Vuex from 'vuex'

import { fetchResults, loginUser, fetchSkills, updateSkill, deleteSkill, createSkill } from '@/api'
import { isValidJWT } from '@/utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    jwt: "",
    currentResults: [],
    currentQuestion: "There are no bad questions.",
    availableSkills: [],
    mySkills: [],
    queryOptions:  {
      selectedSkills: [],
      maxQuerriedSkills: 3,
      maxResultsPerSkill: 10
    },
    flags: {
      initialisedSelectedSkills: false
    }
  },

  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentResults = payload.results
    },
    setSelectedSkillsToAvailableSkills(state) {
      if (!state.flags.initialisedSelectedSkills) {
        state.queryOptions.selectedSkills = state.availableSkills.map(skill => skill.name)
        state.flags.initialisedSelectedSkills = true
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
    isAuthenticated(state) {
      return isValidJWT(state.jwt)
    }
  }
})
