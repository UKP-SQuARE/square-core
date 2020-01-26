import Vue from 'vue'
import Vuex from 'vuex'

import { fetchResults, loginUser, fetchSkills } from '@/api'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    username: "",
    currentResults: [],
    currentQuestion: "There are no bad questions.",
    availableSkills: []
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
        .then(() => context.commit("setUsername", {username: username}))
    },
    signout(context) {
      context.commit("setUsername", {username: ""})
    },
    updateAvailableSkills(context){
      return fetchSkills()
        .then((response) => context.commit("setAvailableSkills", {availableSkills: response}))
    }
  },

  modules: {

  }
})
