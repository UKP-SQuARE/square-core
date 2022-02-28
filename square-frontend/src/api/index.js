/**
 * Contains all API calls
 * Endpoint documentation is found in the documentation of the backend and skill server
 */
import axios from 'axios'

/**
 * URLs to the SQuARE backend servers
 */
let API_URL = process.env.VUE_APP_BACKEND_URL
let SKILL_URL = process.env.VUE_APP_SKILL_MANAGER_URL

/**
 * Register a new user 
 * @param {String} username the username for the new user
 * @param {String} password the password for the new user
 */
export function postSignUp(username, password) {
    return axios.post(`${API_URL}/register`, { username: username, password: password })
}

/**
 * Login the user with the given credentials.
 * Success will results in a JWT for further authentication.
 * @param {String} username the username     
 * @param {String} password the password of the user 
 */
export function postSignIn(username, password) {
    return axios.post(`${API_URL}/login`, { username: username, password: password })
}

/**
 * Get a list of available skill types.
 */
export function getSkillTypes() {
    return axios.get(`${SKILL_URL}/skill-types`)
}

/**
 * Get a list of available skills. 
 * The user name is only required for unpublished skills of the user. Published skills are available without.
 * @param {String} user_name optional user_name for skill selection
 */
export function getSkills(user_name) {
    return axios.get(`${SKILL_URL}/skill?user_id=${user_name}`)
}

/**
 * Get a single skill.
 * @param {String} skillId ID of the skill
 */
export function getSkill(skillId) {
    return axios.get(`${SKILL_URL}/skill/${skillId}`)
}

/**
 * Permanently deletes the skill with the given ID.
 * @param {String} skillId ID of the skill that will be deleted
 */
export function deleteSkill(skillId) {
    return axios.delete(`${SKILL_URL}/skill/${skillId}`)
}

/**
 * Updates the skill with the given ID with the new values. 
 * Only skills with owner ID as specified in JWT can be updated.
 * @param {String} skillId ID of the skill that will be updated
 * @param {Object} newSkill the new values for the skill. All fields need to be present. If a value should not be updated, then set the old value there.
 */
export function putSkill(skillId, newSkill) {
    return axios.put(`${SKILL_URL}/skill/${skillId}`, newSkill)
}

/**
 * Sends a question to the backend and receives the resulting answers
 * @param {String} question the asked question
 * @param {String} context the provided context
 * @param {Object} options the options for the request
 * @param {String} user_id the user id (if available)
 */
export function postQuery(question, context, options, user_id) {
    let data = {
        query: question,
        skill_args: {},
        num_results: options.maxResultsPerSkill,
        user_id: user_id
    }
    if (context.length > 0) {
        data.skill_args.context = context
    }
    let results = options.selectedSkills.map(skillId => axios.post(`${SKILL_URL}/skill/${skillId}/query`, data))
    return axios.all(results)
}

/**
 * Creates a new skill for the owner as specified in JWT.
 * @param {Object} newSkill the values for the new skill
 */
export function postSkill(newSkill) {
    return axios.post(`${SKILL_URL}/skill`, newSkill)
}

/**
 * Ping skill server to check for availability.
 * @param {String} skillUrl URL to the skill server. Format: {scheme}://host[:port]/{base_path}
 */
export function pingSkill(skillUrl) {
    return axios.get(`${SKILL_URL}/health/skill-heartbeat`, { params: { skill_url: skillUrl } })
}
