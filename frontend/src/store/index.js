/**
 * Vuex Store. Global state of the application is managed here.
 */
import axios from 'axios'
import Vue from 'vue'
import Vuex from 'vuex'

import {
  postQuery,
  getSkills,
  putSkill,
  deleteSkill,
  postSkill,
  getDatastoreIndices,
  getDatastores
} from '../api'

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
    availableDatastores:[],
    availableDatastoresName:[],
    availableIndices:[],
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
    inputMode: false,
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
    setDatastores(state, payload) {
      state.availableDatastores = payload.datastores

    },

    setIndices(state, payload) {
      state.availableDatastores.forEach(datastore=>{
        if (datastore.name==payload.dataStoreId){
          datastore.indices=payload.indices

        }
      })

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
    },
    changeInputMode(state) {
      state.inputMode = !state.inputMode
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
    updateDatastores(context) {
      return getDatastores(context.getters.authenticationHeader())
          .then((response) => context.commit('setDatastores', { datastores: response.data }))
    },
    updateIndices(context) {
      //console.log(context.state.availableDatastores)
      context.state.availableDatastores.forEach(datastore=>{context.state.availableDatastoresName.push(datastore.name)} )
      //console.log(context.state.availableDatastoresName)
      context.state.availableDatastoresName.forEach(datastoreName=>{getDatastoreIndices(context.getters.authenticationHeader(), datastoreName)
          .then((response) => {
            context.commit('setIndices', { indices: response.data, dataStoreId:datastoreName })
          }
          ) })
   
      //console.log("Update indices")   
   
      
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
        return {'Authorization': `Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIyUmE2VkdrUTdSNkJ3STk5WVpBLVJVQWhaaS12TlJmcTVLam11SXVMbkVZIn0.eyJleHAiOjE2NzUzNDYxOTAsImlhdCI6MTY3NTM0NTg5MCwianRpIjoiYjM5N2QyZTAtNjE1Ny00NjcyLWFjZjMtMWM5N2FkNDZlMGYzIiwiaXNzIjoiaHR0cHM6Ly9zcXVhcmUudWtwLWxhYi5kZS9hdXRoL3JlYWxtcy9zcXVhcmUiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiYjhmZWNlMTEtYWM0Yi00ZDRhLWJiYzktMWU5OGMzNzMzOWFiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibW9kZWxzIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXNxdWFyZSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJjbGllbnRJZCI6Im1vZGVscyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6IjEwLjE2Ny4xLjI1NCIsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1tb2RlbHMiLCJjbGllbnRBZGRyZXNzIjoiMTAuMTY3LjEuMjU0In0.dxJ_ASFPmU5ojzDDAptdV2tODwqSlnrvZAU01IuTEIXVhsdEu2QED3cXjJMklMCW9xitwThhGDEDB4Cp3Lr2H8Iv-bEZ1XM5zEBfUka01ZOBv8JSZBQyCzGx42cHdhiM24jP-zvVwyhfVrL6XiuzeGdglaug9RLGzuhpsqIoT4RwYk4g34Hj3k7hSbx2ZV1J8PD6F69qTZcHrTzMgZoZkE2ctXC5V0XnAyP_XyoelvctcePcch9knIOjnCzygUoZ42yKx6pAOVuhlvQ9imZF9HeQcKhIKFKjFis1G2q1R2tchXs7S_bX9jQfAtv984cz0hHselO90r2oI6CgBYRv8w`}

      }
    }
  }
})
