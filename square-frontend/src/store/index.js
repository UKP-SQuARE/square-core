/**
 * Vuex Store. Global state of the application is managed here.
 */
import axios from 'axios'
import Vue from 'vue'
import Vuex from 'vuex'

import { postQuery, postSignIn, getSkills, putSkill, deleteSkill, postSkill } from '@/api'

Vue.use(Vuex)

const LOCALSTORAGE_KEY_JWT = 'jwt'

export default new Vuex.Store({
  /**
   * State contains all variables that
   * 1) are accessed and changed in multiple components
   * 2) should be restored when a view is changed and later returned to
   */
  state: {
    user: {},
    // JWT is also stored in LocalStorage 
    jwt: '',
    currentResults: [],
    currentQuestion: '',
    currentContext: '',
    availableSkills: [],
    // Subset of availableSkills with owner_id equal to id in jwt
    mySkills: [],
    queryOptions: {
      selectedSkills: Array(3).fill('None'),
      maxResultsPerSkill: 10
    },
    explainOptions: {
      selectedSkill: ''
    },
    // Control flags
    flags: {
      initialisedExplainOptions: false
    }
  },
  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentContext = payload.context
      state.currentResults = payload.results
    },
    initExplainOptions(state, payload) {
      // Default value for selected skills should be all available skills
      if (!state.flags.initialisedExplainOptions || payload.forceSkillInit) {
        if (state.availableSkills.length > 0) {
          state.explainOptions.selectedSkill = state.availableSkills[0].id
        }
        state.flags.initialisedExplainOptions = true
      }
    },
    setSkills(state, payload) {
      let tmp = state.availableSkills.length
      state.availableSkills = payload.skills
      if (state.user.name) {
        state.mySkills = state.availableSkills.filter(skill => skill.user_id === state.user.name)
      }
      // We want to reset selected skills if more skills are available (due to sign in mostly)
      if (tmp !== state.availableSkills.length) {
        state.flags.initialisedQueryOptions = false
        state.flags.initialisedExplainOptions = false
      }
    },
    /**
     * Set the JWT and all derived values
     */
    setJWT(state, payload) {
      localStorage.setItem(LOCALSTORAGE_KEY_JWT, payload.jwt)
      state.jwt = payload.jwt
      if (payload.jwt && payload.jwt.split('.').length === 3) {
        let data = JSON.parse(atob(payload.jwt.split('.')[1]))
        state.user = data.sub
      }
    },
    setQueryOptions(state, payload) {
      state.queryOptions = payload.queryOptions
    }
  },
  /**
   * Mostly wrappers around API calls that manage committing the received results
   */
  actions: {
    query(context, { question, inputContext, options }) {
      options.maxResultsPerSkill = parseInt(options.maxResultsPerSkill)
      let user_id = context.state.user.name ? context.state.user.name : ''
      return postQuery(question, inputContext, options, user_id)
          .then(axios.spread((...responses) => {
            // Map responses to a list with the skill metadata and predictions combined
            let results = responses.map((response, index) => ({
              skill: context.state.availableSkills.filter(skill => skill.id === options.selectedSkills[index])[0],
              predictions: response.data.predictions
            }))
            context.commit('setAnsweredQuestion', { results: results, question: question, context: inputContext })
            context.commit('setQueryOptions', { queryOptions: options })
          }))
    },
    signIn(context, { username, password }) {
      return postSignIn(username, password)
          .then((response) => {
            context.commit('setJWT', { jwt: response.data.token })
          }).then(() => context.dispatch('updateSkills'))
    },
    signOut(context) {
      // Reset JWT and (private) skills
      context.commit('setJWT', { jwt: '' })
      context.commit('setSkills', { skills: [] })
    },
    initJWTfromLocalStorage(context) {
      let jwt = localStorage.getItem(LOCALSTORAGE_KEY_JWT) || ''
      context.commit('setJWT', { jwt: jwt })
    },
    updateSkills(context) {
      let user_name = context.state.user.name ? context.state.user.name : ''
      return getSkills(user_name)
          .then((response) => context.commit('setSkills', { skills: response.data }))
    },
    updateSkill(context, { skill }) {
      return putSkill(skill.id, skill)
          .then(() => context.dispatch('updateSkills'))
    },
    createSkill(context, { skill }) {
      return postSkill(skill)
          .then(() => context.dispatch('updateSkills'))
    },
    deleteSkill(context, { skillId }) {
      return deleteSkill(skillId)
          .then(() => context.dispatch('updateSkills'))
    }
  },
  /**
   * Getters for information not stored as state variables
   */
  getters: {
    /**
     * Check if the JWT is valid
     */
    isAuthenticated: (state) => () => {
      let jwt = state.jwt
      if (!jwt || jwt.split('.').length < 3) {
        return false
      }
      let data = JSON.parse(atob(jwt.split('.')[1]))
      return new Date() < new Date(data.exp * 1000)
    },
    /**
     * Check if the JWT is expired
     */
    isSessionExpired: (state) => () => {
      let jwt = state.jwt
      if (!jwt || jwt.split('.').length < 3) {
        return false
      }
      let data = JSON.parse(atob(jwt.split('.')[1]))
      return new Date() >= new Date(data.exp * 1000)
    }
  }
})
