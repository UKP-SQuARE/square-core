const results = [
    {
        skillName: "CQA",
        results: ["Hello", "this is a test", "a third thing"]
    },
    {
        skillName: "KQA",
        results: ["Yes", "no", "maybe"]
    }
]

const skills = ["CQA", "KQA"]

export function fetchResults(question, options) {
    return new Promise((resolve) => {
        setTimeout(() => {
            if (question.length > 0 && options) {
                resolve(results)
            } else {
                resolve(results)
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
                resolve()
            }
        }, 200)
    })
}

export function fetchSkills() {
    return new Promise((resolve) => {
        setTimeout(() => {
                resolve(skills)
        }, 200)
    })
}