/**
 * Vuex Store. Global state of the application is managed here.
 */
import axios from 'axios'
import Vue from 'vue'
import Vuex from 'vuex'

import { postQuery, getToken, getSkills, putSkill, deleteSkill, postSkill } from '../api'

Vue.use(Vuex)

const LOCALSTORAGE_KEY_ACCESS_TOKEN = 'accessToken'
const LOCALSTORAGE_KEY_REFRESH_TOKEN = 'refreshToken'

export default new Vuex.Store({
  /**
   * State contains all variables that
   * 1) are accessed and changed in multiple components
   * 2) should be restored when a view is changed and later returned to
   */
  state: {
    authentication: {
      data: {},
      accessToken: '',
      refreshToken: ''
    },
    currentResults: [],
    currentQuestion: '',
    currentContext: '',
    availableSkills: [],
    mySkills: [],
    skillOptions: {
      qa: {
        selectedSkills: Array(3).fill('None'),
        maxResultsPerSkill: 10
      },
      explain: {
        selectedSkills: Array(3).fill('None')
      }
    }
  },
  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentContext = payload.context
      state.currentResults = payload.results
    },
    setSkills(state, payload) {
      state.availableSkills = payload.skills
      if (state.authentication.data) {
        state.mySkills = state.availableSkills.filter(skill => skill.user_id === state.authentication.data.preferred_username)
      }
    },
    /**
     * Set the access token and all derived values
     */
    setAuthentication(state, payload) {
      localStorage.setItem(LOCALSTORAGE_KEY_ACCESS_TOKEN, payload.accessToken)
      localStorage.setItem(LOCALSTORAGE_KEY_REFRESH_TOKEN, payload.refreshToken)
      state.authentication.accessToken = payload.accessToken
      state.authentication.refreshToken = payload.refreshToken
      if (payload.accessToken) {
        state.authentication.data = JSON.parse(atob(payload.accessToken.split('.')[1]))
      }
    },
    setSkillOptions(state, payload) {
      state.skillOptions[payload.selectorTarget] = payload.skillOptions
    }
  },
  /**
   * Mostly wrappers around API calls that manage committing the received results
   */
  actions: {
    query(context, { question, inputContext, options }) {
      options.maxResultsPerSkill = parseInt(options.maxResultsPerSkill)
      let userId = context.state.authentication.data ? context.state.authentication.data.preferred_username : ''
      return postQuery(context.getters.authenticationHeader(), question, inputContext, options, userId)
          .then(axios.spread((...responses) => {
            // Map responses to a list with the skill metadata and predictions combined
            let results = responses.map((response, index) => ({
              skill: context.state.availableSkills.filter(skill => skill.id === options.selectedSkills[index])[0],
              predictions: response.data.predictions
            }))
            context.commit('setAnsweredQuestion', { results: results, question: question, context: inputContext })
          }))
    },
    signIn(context, { code, redirectURI, clientId }) {
      return getToken(code, redirectURI, clientId)
          .then((response) => {
            context.commit('setAuthentication', {
              accessToken: response.data.accessToken,
              refreshToken: response.data.refreshToken
            })
          }).then(() => context.dispatch('updateSkills'))
    },
    signOut(context) {
      // Reset authentication and (private) skills
      context.commit('setAuthentication', { accessToken: '', refreshToken: '' })
      context.commit('setSkills', { skills: [] })
    },
    authenticationFromLocalStorage(context) {
      let accessToken = localStorage.getItem(LOCALSTORAGE_KEY_ACCESS_TOKEN) || ''
      let refreshToken = localStorage.getItem(LOCALSTORAGE_KEY_REFRESH_TOKEN) || ''
      context.commit('setAuthentication', { accessToken: accessToken, refreshToken: refreshToken })
    },
    selectSkill(context, { skillOptions, selectorTarget }) {
      context.commit('setSkillOptions', { skillOptions: skillOptions, selectorTarget: selectorTarget })
    },
    updateSkills(context) {
      let userId = context.state.authentication.data ? context.state.authentication.data.preferred_username : ''
      return getSkills(context.getters.authenticationHeader(), userId)
          .then((response) => context.commit('setSkills', { skills: response.data }))
    },
    updateSkill(context, { skill }) {
      return putSkill(context.getters.authenticationHeader(), skill.id, skill)
          .then(() => context.dispatch('updateSkills'))
    },
    createSkill(context, { skill }) {
      return postSkill(context.getters.authenticationHeader(), skill)
          .then(() => context.dispatch('updateSkills'))
    },
    deleteSkill(context, { skillId }) {
      return deleteSkill(context.getters.authenticationHeader(), skillId)
          .then(() => context.dispatch('updateSkills'))
    }
  },
  /**
   * Getters for information not stored as state variables
   */
  getters: {
    /**
     * Check if the access token is valid
     */
    isAuthenticated: (state) => () => {
      if (!state.authentication.accessToken) {
        return false
      } else {
        return new Date() < new Date(state.authentication.data.exp * 1000)
      }
    },
    authenticationHeader: (state, getters) => () => {
      if (!getters.isAuthenticated()) {
        return {}
      } else {
        return {'Authorization': `${state.authentication.data.typ} ${state.authentication.accessToken}`}
      }
    }
  }
})
