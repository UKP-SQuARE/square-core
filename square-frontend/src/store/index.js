/**
 * Vuex Store. Global state of the application is managed here.
 */
import axios from 'axios'
import Vue from 'vue'
import Vuex from 'vuex'

import { postQuery, getSkills, putSkill, deleteSkill, postSkill } from '../api'

Vue.use(Vuex)

export default new Vuex.Store({
  /**
   * State contains all variables that
   * 1) are accessed and changed in multiple components
   * 2) should be restored when a view is changed and later returned to
   */
  state: {
    userInfo: {},
    token: '',
    currentResults: [],
    currentQuestion: '',
    currentContext: '',
    currentChoices: [],
    currentSkills: [],
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
    },
    loadingExplainability: false,
    attackResults: [],
  },
  mutations: {
    setAnsweredQuestion(state, payload) {
      state.currentQuestion = payload.question
      state.currentContext = payload.context
      state.currentChoices = payload.choices
      state.currentResults = payload.results
      state.currentSkills = payload.skills
    },
    setAttack(state, payload) {
      state.attackResults = payload.results
    },
    setSkills(state, payload) {
      state.availableSkills = payload.skills
      if (state.userInfo.preferred_username) {
        state.mySkills = state.availableSkills.filter(skill => skill.user_id === state.userInfo.preferred_username)
      }
    },
    setAuthentication(state, payload) {
      if (payload.userInfo) {
        state.userInfo = payload.userInfo
      }
      state.token = payload.token
    },
    setSkillOptions(state, payload) {
      state.skillOptions[payload.selectorTarget] = payload.skillOptions
    },
    setLoadingExplainability(state, payload) {
      state.loadingExplainability = payload.value
    }
  },
  /**
   * Mostly wrappers around API calls that manage committing the received results
   */
  actions: {
    query(context, { question, inputContext, choices, options }) {
      options.maxResultsPerSkill = parseInt(options.maxResultsPerSkill)
      // if explain_kwargs in options
      var timeoutExplainabilityLoading = null
      if ( "explain_kwargs" in options ){
        timeoutExplainabilityLoading = setTimeout(() => {
          context.commit('setLoadingExplainability', {'value': true});
        }, 8000);
      }
      return postQuery(context.getters.authenticationHeader(), question, inputContext, choices, options)
          .then(axios.spread((...responses) => {
            // Map responses to a list with the skill metadata and predictions combined
            let results = responses.map((response, index) => ({
              skill: context.state.availableSkills.filter(skill => skill.id === options.selectedSkills[index])[0],
              predictions: response.data.predictions,
              adversarial: response.data.adversarial
            }))
            context.commit('setAnsweredQuestion', { results: results, 
                                                    question: question, 
                                                    context: inputContext, 
                                                    choices: choices, 
                                                    skills: options.selectedSkills })
          })).finally(() => {
            if ( "explain_kwargs" in options ){
              clearTimeout(timeoutExplainabilityLoading);
              context.commit('setLoadingExplainability', {'value': false});
            }
          })
    },
    attack(context, { question, inputContext, choices, options }) {
      options.maxResultsPerSkill = parseInt(options.maxResultsPerSkill)
      return postQuery(context.getters.authenticationHeader(), question, inputContext, choices, options)
          .then(axios.spread((...responses) => {
            // Map responses to a list with the skill metadata and predictions combined
            let results = responses.map((response, index) => ({
              skill: context.state.availableSkills.filter(skill => skill.id === options.selectedSkills[index])[0],
              predictions: response.data.predictions,
              adversarial: response.data.adversarial
            }))
            context.commit('setAttack', { results: results,
                                          question: question,
                                          context: inputContext,
                                          choices: choices,
                                          skills: options.selectedSkills })
          }))
    },
    signIn(context, { userInfo, token }) {
      context.commit('setAuthentication', { userInfo: userInfo, token: token })
    },
    refreshToken(context, { token }) {
      context.commit('setAuthentication', { token: token })
    },
    signOut(context) {
      // Reset user info and (private) skills
      context.commit('setAuthentication', { userInfo: {}, token: '' })
      context.commit('setSkills', { skills: [] })
    },
    selectSkill(context, { skillOptions, selectorTarget }) {
      context.commit('setSkillOptions', { skillOptions: skillOptions, selectorTarget: selectorTarget })
    },
    updateSkills(context) {
      return getSkills(context.getters.authenticationHeader())
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
  getters: {
    authenticationHeader: (state) => () => {
      if (state.token) {
        return {'Authorization': `Bearer ${state.token}`}
      } else {
        return {}
      }
    }
  }
})
