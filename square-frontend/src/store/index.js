/**
 * Vuex Store. Global state of the application is managed here.
 */
import Vue from 'vue'
import Vuex from 'vuex'

import { fetchResults, loginUser, fetchSkills, updateSkill, deleteSkill, createSkill, fetchSelectors } from '@/api'

Vue.use(Vuex)

const LOCALSTORAGE_KEY_JWT = 'jwt'

export default new Vuex.Store({
  /**
   * State contains all variables that
   * 1) are accessed and changed in multiple components
   * 2) should be restored when a view is changed and later returned to
   */
  state: {
    user: '',
    // JWT is also stored in LocalStorage 
    jwt: '',
    currentResults: [],
    currentQuestion: '',
    currentContext: '',
    availableSkills: [],
    // Subset of availableSkills with owner_id equal to id in jwt
    mySkills: [],
    availableSkillSelectors: [],
    queryOptions: {
      selector: '',
      selectedSkills: [],
      maxQuerriedSkills: 3,
      maxResultsPerSkill: 10,
      skillArgs: {}
    },
    // Control flags
    flags: {
      initialisedSelectedSkills: false,
      initialisedSelector: false
    }
  },
  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentContext = payload.context
      state.currentResults = payload.results
    },
    initQueryOptions(state, payload) {
      let forceSkillInit = payload.forceSkillInit
      // Default value for selected skills should be all available skills
      if (!state.flags.initialisedSelectedSkills || forceSkillInit) {
        state.queryOptions.selectedSkills = state.availableSkills.map(skill => { return skill.name })
        state.flags.initialisedSelectedSkills = true
      }
      // Value for selector should be set to a selector.
      if (!state.flags.initialisedSelector) {
        state.queryOptions.selector = state.availableSkillSelectors[0].name
        state.flags.initialisedSelector = true
      }
    },
    setSkills(state, payload) {
      const lenSkills = state.availableSkills.length
      state.availableSkills = payload.skills
      if (state.user) {
        state.mySkills = payload.skills.filter(skill => skill.owner_id === state.user.id)
      }
      // We want to reset selected skills if more skills are available (due to login mostly)
      if (lenSkills !== state.availableSkills.length) {
        state.flags.initialisedSelectedSkills = false
      }
    },
    /**
     * Set the JWT and all derived values
     */
    setJWT(state, payload) {
      localStorage.setItem(LOCALSTORAGE_KEY_JWT, payload.jwt)
      state.jwt = payload.jwt
      if (payload.jwt && payload.jwt.split('.').length === 3) {
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
  /**
   * Mostly wrappers around API calls that manage committing the received results
   */
  actions: {
    query(context, { question, inputContext, options }) {
      // we get these as strings; parse them back to int
      options.maxQuerriedSkills = parseInt(options.maxQuerriedSkills)
      options.maxResultsPerSkill = parseInt(options.maxResultsPerSkill)
      let user_id = context.state.user ? context.state.user.id : ''
      return fetchResults(question, inputContext, options, user_id)
          .then((response) => {
            context.commit('setAnsweredQuestion', { results: response.data, question: question, context: inputContext })
            context.commit('setQueryOptions', { queryOptions: options })
          })
    },
    login(context, { username, password }) {
      return loginUser(username, password)
          .then((response) => {
            context.commit('setJWT', { jwt: response.data.token })
          })
    },
    signout(context) {
      context.commit('setJWT', { jwt: '' })
    },
    initJWTfromLocalStorage(context) {
      var jwt = localStorage.getItem(LOCALSTORAGE_KEY_JWT) || ''
      context.commit('setJWT', { jwt: jwt })
    },
    updateSkills(context) {
      var jwt = ''
      if (context.getters.isAuthenticated()) {
        jwt = context.state.jwt
      }
      return fetchSkills(jwt)
          .then((response) => context.commit('setSkills', { skills: response.data }))
    },
    updateSelectors(context) {
      return fetchSelectors()
          .then((response) => context.commit('setSelectors', { selectors: response.data }))
    },
    updateSkill(context, { skill }) {
      return updateSkill(skill.id, skill, context.state.jwt)
          .then(() => context.dispatch('updateSkills'))
    },
    createSkill(context, { skill }) {
      return createSkill(skill, context.state.jwt)
          .then(() => context.dispatch('updateSkills'))
    },
    deleteSkill(context, { skillId }) {
      return deleteSkill(skillId, context.state.jwt)
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
      let exp = new Date(data.exp * 1000)
      let now = new Date()
      return now < exp
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
      let exp = new Date(data.exp * 1000)
      let now = new Date()
      return now >= exp
    }
  }
})
