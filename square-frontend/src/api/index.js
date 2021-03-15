/**
 * Contains all API calls
 * Endpoint documentation is found in the documentation of the backend and skill server
 */
import axios from "axios"

/**
 * URL to the SQuARE backend server
 */
var API_URL = process.env.VUE_APP_BACKEND_URL

/**
 * Sends a question to the backend and receives the resulting answers
 * @param {String} question the asked question
 * @param {Object} options the options for the request
 */
export function fetchResults(question, options) {
    return axios.post(`${API_URL}/question`, { question: question, options: options })
}

/**
 * Register a new user 
 * @param {String} username the username for the new user
 * @param {String} password the password for the new user
 * @param {String} email the email for the new user
 */
export function registerUser(username, password, email) {
    return axios.post(`${API_URL}/register`, { username: username, password: password,email:email })
}

/**
 * Login the user with the given credentials.
 * Success will result in a JWT for further authentication.
 * @param {String} username the username     
 * @param {String} password the password of the user 
 */
export function loginUser(username, password) {
    return axios.post(`${API_URL}/login`, { username: username, password: password })
}

/**
 * Create and send reset password link.
 * Success will result in a JWT for further authentication.
 * @param {String} token the registered email
 */
export function confirmEmail(token) {
    return axios.post(`${API_URL}/confirmEmail`, { token: token})
}

/**
 * Create and send reset password link.
 * Success will result in a JWT for further authentication.
 * @param {String} email the registered email
 */
export function requestresetPassword(email) {
    return axios.post(`${API_URL}/requestresetPassword`, { email: email})
}

/**
 * Reset password for registered user.
 * Success will result in a JWT for further authentication.
 * @param {String} token the registered email
 * @param {String} password the new password of the user
 */
export function validatenewPassword(token,password) {
    return axios.post(`${API_URL}/validatenewPassword`, { token: token, password:password})
}

/**
 * Get a list of possible skill selectors that the backend supports
 */
export function fetchSelectors() {
    return axios.get(`${API_URL}/selectors`)
}

/**
 * Get a list of available skills. 
 * The JWT is only required for unpublished skills of the user. Published skills are available without token.
 * @param {String} jwt optional JWT for authentication
 */
export function fetchSkills(jwt) {
    if (jwt) {
        return axios.get(`${API_URL}/skills`, { headers: { Authorization: `Bearer ${jwt}` } })
    } else {
        return axios.get(`${API_URL}/skills`)
    }
}

/**
 * Permanently deletes the skill with the given ID. Only skills with owner ID as specified in JWT can be deleted.
 * @param {String} skillId ID of the skill that will be deleted
 * @param {String} jwt JWT for authentication of skill ownership
 */
export function deleteSkill(skillId, jwt) {
    return axios.delete(`${API_URL}/skill/${skillId}`, { headers: { Authorization: `Bearer ${jwt}` } })
}

/**
 * Updates the skill with the given ID with the new values. 
 * Only skills with owner ID as specified in JWT can be updated.
 * @param {String} skillId ID of the skill that will be deleted
 * @param {Object} newSkill the new values for the skill. All fields need to be present. If a value should not be updated, then set the old value there.
 * @param {String} jwt JWT for authentication of skill ownership
 */
export function updateSkill(skillId, newSkill, jwt) {
    return axios.post(`${API_URL}/skill/${skillId}`, newSkill, { headers: { Authorization: `Bearer ${jwt}` } })
}

/**
 * Creates a new skill for the owner as specified in JWT.
 * @param {Object} newSkill the values for the new skill
 * @param {String} jwt JWT for authentication
 */
export function createSkill(newSkill, jwt) {
    return axios.post(`${API_URL}/skill`, newSkill, { headers: { Authorization: `Bearer ${jwt}` } })
}

/**
 * Ping skill server to check for availability.
 * @param {String} skillUrl URL to the skill server. Format: {scheme}://host[:port]/{base_path}
 */

export function pingSkill(skillUrl) {
     return axios.get(`${skillUrl}/ping`)
}

/**
 * Train a skill belonging to the user  with  provided training data. JWT required
 * Only skills with owner ID as specified in JWT can be updated.
 * @param {String} skillId ID of the skill that will be trained
 * @param {FormData} files training and validation fle for training the skill. All files need to be preseent
 * @param {String} jwt JWT for authentication of skill ownership
 */
export function trainSkill(skillId, files, jwt) {
    return axios.post(`${API_URL}/skill/${skillId}/train`, files,
        {headers: { Authorization: `Bearer ${jwt}`,
                    "Content-Type": "multipart/form-data"}})
}