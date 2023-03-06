/**
 * Contains all API calls
 * Endpoint documentation is found in the documentation of the backend and skill server
 */
import axios from 'axios'

/**
 * URLs to the SQuARE backend servers
 */
const SKILL_URL = `${process.env.VUE_APP_SKILL_MANAGER_URL}`
const EVALUATOR_URL = `${process.env.VUE_APP_EVALUATOR_URL}`
const DATASTORES_URL = `${process.env.VUE_APP_DATASTORES_URL}`

/**
 * Get a list of available skill types.
 * @param {Object} headers optional authentication header
 */
export function getSkillTypes(headers) {
    return axios.get(`${SKILL_URL}/skill-types`, { headers: headers })
}

/**
 * Get a list of available datasets.
 * @param {Object} headers optional authentication header
 */
export function getDataSets(headers) {
    return axios.get(`${EVALUATOR_URL}/dataset`, { headers: headers })
}

/**
 * Get a list of available datastores
 * @param {Object} headers optional authentication header
 */
export function getDatastores(headers) {
    return axios.get(`${DATASTORES_URL}`, { headers: headers })
}

/**
 * Get a list of all indices of a datastore
 * @param {Object} headers optional authentication header
 */
export function getDatastoreIndices(headers, datastoreId) {
    return axios.get(`${DATASTORES_URL}/${datastoreId}/indices`, { headers: headers })
}


/**
 * Get a list of available skills. 
 * The user name is only required for unpublished skills of the user. Published skills are available without.
 * @param {Object} headers optional authentication header
 */
export function getSkills(headers) {
    return axios.get(`${SKILL_URL}/skill`, { headers: headers })
}

/**
 * Get a single skill.
 * @param {Object} headers optional authentication header
 * @param {String} skillId ID of the skill
 */
export function getSkill(headers, skillId) {
    return axios.get(`${SKILL_URL}/skill/${skillId}`, { headers: headers })
}

/**
 * Permanently deletes the skill with the given ID.
 * @param {Object} headers optional authentication header
 * @param {String} skillId ID of the skill that will be deleted
 */
export function deleteSkill(headers, skillId) {
    return axios.delete(`${SKILL_URL}/skill/${skillId}`, { headers: headers })
}

/**
 * Updates the skill with the given ID with the new values. 
 * Only skills with owner ID as specified in access token can be updated.
 * @param {Object} headers optional authentication header
 * @param {String} skillId ID of the skill that will be updated
 * @param {Object} newSkill the new values for the skill. All fields need to be present. If a value should not be updated, then set the old value there.
 */
export function putSkill(headers, skillId, newSkill) {
    return axios.put(`${SKILL_URL}/skill/${skillId}`, newSkill, { headers: headers })
}

/**
 * Sends a question to the backend and receives the resulting answers
 * @param {Object} headers optional authentication header
 * @param {String} question the asked question
 * @param {String} context the provided context
 * @param {Object} options the options for the request
 */
export function postQuery(headers, question, context, choices, options) {
    let data = {
        query: question,
        skill_args: {},
        explain_kwargs: {},
        attack_kwargs: {},
        feedback_documents: [],
        num_results: options.maxResultsPerSkill
    }
    if (context.length > 0) {
        data.skill_args.context = context
    }
    if (choices.length > 0) {
        data.skill_args.choices = choices
    }
    if (options.explain_kwargs) {
        data.explain_kwargs = {
            "method": options.explain_kwargs.method,
            "top_k": options.explain_kwargs.top_k,
            "mode": options.explain_kwargs.mode
        }
    }
    if (options.attack_kwargs) {
        data.attack_kwargs = {
            "method": options.attack_kwargs.method,
            "saliency_method": options.attack_kwargs.saliency_method,
            "max_flips": options.attack_kwargs.max_flips,
            "max_reductions": options.attack_kwargs.max_reductions,
            "max_tokens": options.attack_kwargs.max_tokens,
        }
    }
    data.preprocessing_kwargs = { "max_length": 512 }

    if (options.feedback_documents) {
        data.skill_args.feedback_documents = options.feedback_documents
    }
    let results = options.selectedSkills.map(skillId => {
        return axios.post(`${SKILL_URL}/skill/${skillId}/query`, data, { headers: headers })
    })
    return axios.all(results)
}

/**
 * Creates a new skill for the owner as specified in the authentication header.
 * @param {Object} headers optional authentication header
 * @param {Object} newSkill the values for the new skill
 */
export function postSkill(headers, newSkill) {
    return axios.post(`${SKILL_URL}/skill`, newSkill, { headers: headers })
}

/**
 * Ping skill server to check for availability.
 * @param {Object} headers optional authentication header
 * @param {String} skillUrl URL to the skill server. Format: {scheme}://host[:port]/{base_path}
 */
export function pingSkill(headers, skillUrl) {
    headers.params = { skill_url: skillUrl }
    return axios.get(`${SKILL_URL}/health/skill-heartbeat`, headers)
}

/**
 * Get leaderboard data.
 * @param {String} dataset_name Name of the dataset to get the leaderboard for.
 * @param {String} metric_name Name of the metric to get the leaderboard for.
 * @param {Object} headers Authentication header
 */
export function getLeaderboard(dataset_name, metric_name, headers) {
    return axios.get(`${EVALUATOR_URL}/leaderboard/${dataset_name}/${metric_name}`, { headers: headers })
}

/**
 * Get all user and public evaluations.
 * @param {Object} headers Authentication header
 */
 export function getEvaluations(headers) {
    return axios.get(`${EVALUATOR_URL}/evaluations`, { headers: headers })
}

/**
 * Get all metrics. Not yet implemented in backend.
 * @param {Object} headers Authentication header
 */
 export function getMetrics(headers) {
    return axios.get(`${EVALUATOR_URL}/metrics`, { headers: headers })
}

/**
 * Run evaluation with skill_id, dataset_name and metric_name
 * @param {Object} headers Authentication header
 */
 export function runEvaluation(headers, skill_id, dataset_name, metric_name) {
    return axios.post(`${EVALUATOR_URL}/evaluate/${skill_id}/${dataset_name}/${metric_name}`, {}, { headers: headers })
}