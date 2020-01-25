const results = ["Hello", "this is a test", "a third thing"]

export function fetchResults() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(results)
        }, 100)
    })
}