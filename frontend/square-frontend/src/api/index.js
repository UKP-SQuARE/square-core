const results = [
    {
        name: "CQA",
        results: ["Hello", "this is a test", "a third thing"]
    },
    {
        name: "KQA",
        results: ["Yes", "no", "maybe"]
    }
]

const skills = [{
    id: "1",
    owner_id: "1",
    name: "CQA",
    is_published: true,
    scheme: "http",
    host: "localhost",
    base_path: "api"
},
{
    id: "2",
    owner_id: "2",
    name: "KQA",
    is_published: true,
    scheme: "http",
    host: "localhost",
    base_path: "api"
}]

const my_skills = [{
    id: "1",
    owner_id: "1",
    name: "CQA",
    is_published: true,
    scheme: "http",
    host: "localhost",
    base_path: "api"
}]

export function fetchResults(question, options) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (options && question.lastIndexOf("?")!=-1) {
                resolve(results)
            } else {
                reject("That's not a question")
            }
        }, 200)
    })
}

export function registerUser(username, password) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if(username === "gregor" || password === "hunter13") {
                reject("Username already in use.")
            } else {
                resolve()
            }
        }, 200)
    })
}

export function loginUser(username, password) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if(username != "gregor" && password != "pw") {
                reject("Wrong username or password.")
            } else {
                resolve({data: "token"})
            }
        }, 200)
    })
}

export function fetchAvailableSkills(jwt) {
    return new Promise((resolve) => {
        setTimeout(() => {
            if(jwt) {
                resolve(skills)
            } else {
                resolve(skills)
            }
        }, 200)
    })
}

export function fetchMySkills(jwt) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (jwt.length > 0){
                resolve(my_skills)
            } else {
                reject("Not logged in")
            }
                
        }, 200)
    })
}

export function deleteSkill(skillId, jwt) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
                if(jwt && skillId==="1"){
                    resolve()
                } else {
                    reject("Deletion failed")
                }
        }, 200)
    })
}

export function updateSkill(newSkill, jwt) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
                if(jwt && newSkill.name==="fail"){
                    reject("Update failed")
                } else {
                    resolve()
                }
        }, 200)
    })
}