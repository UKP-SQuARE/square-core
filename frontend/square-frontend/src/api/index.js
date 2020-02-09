import axios from "axios"

const API_URL = "http://127.0.0.1:5000/api"

export function fetchResults(question, options) {
    return axios.post(`${API_URL}/question`, {question: question, options: options})
}

export function registerUser(username, password) {
    return axios.post(`${API_URL}/register`, {username: username, password: password})
}

export function loginUser(username, password) {
    return axios.post(`${API_URL}/login`, {username: username, password: password})
}

export function fetchSelectors() {
    return axios.get(`${API_URL}/selectors`)
}

export function fetchSkills(jwt) {
    if (jwt) {
        return axios.get(`${API_URL}/skills`, {headers: {Authorization: `Bearer ${jwt}`}})
    } else {
        return axios.get(`${API_URL}/skills`)
    }
}

export function deleteSkill(skillId, jwt) {
    return axios.delete(`${API_URL}/skill/${skillId}`, {headers: {Authorization: `Bearer ${jwt}`}})
}

export function updateSkill(skillId, newSkill, jwt) {
    return axios.post(`${API_URL}/skill/${skillId}`, {skill: newSkill}, {headers: {Authorization: `Bearer ${jwt}`}})
}

export function createSkill(newSkill, jwt) {
    return axios.post(`${API_URL}/skill`, {skill: newSkill}, {headers: {Authorization: `Bearer ${jwt}`}})
}