import Vue from 'vue'
import Vuex from 'vuex'

import { fetchResults, loginUser, fetchAvailableSkills, fetchMySkills, updateSkill, deleteSkill } from '@/api'
import { isValidJWT } from '@/utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    username: "",
    jwt: "",
    currentResults: [],
    currentQuestion: "There are no bad questions.",
    availableSkills: [],
    mySkills: [],

  },

  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentResults = payload.results
    },
    setUsername(state, payload){
      state.username = payload.username
    },
    setAvailableSkills(state, payload){
      state.availableSkills = payload.availableSkills
    },
    setMySkills(state, payload){
      state.mySkills = payload.mySkills
    },
    setJWT(state, payload) {
      state.jwt = payload.jwt
    }
  },

  actions: {
    answerQuestion(context, {question, options}) {
      return fetchResults(question, options)
        .then((response) => {
          context.commit("setAnsweredQuestion", {results: response, question: question})
        })
    },
    login(context, {username, password}) {
      return loginUser(username, password)
        .then((response) => {
          context.commit("setUsername", {username: username})
          context.commit("setJWT", {jwt: response.data})
        })
    },
    signout(context) {
      context.commit("setUsername", {username: ""})
      context.commit("setJWT", {jwt: ""})
    },
    updateAvailableSkills(context){
      return fetchAvailableSkills(context.state.jwt)
        .then((response) => context.commit("setAvailableSkills", {availableSkills: response}))
    },
    updateMySkills(context) {
      return fetchMySkills(context.state.jwt)
        .then((response) => context.commit("setMySkills", {mySkills: response}))
    },
    updateSkill(context, {skill}) {
      return updateSkill(skill, context.state.jwt)
    },
    deleteSkill(context, {skillId}) {
      return deleteSkill(skillId, context.state.jwt)
        .then(() => context.dispatch("updateMySkills"))
    }
  },

  getters: {
    isAuthenticated(state) {
      return isValidJWT(state.jwt)
    }
  }
})
