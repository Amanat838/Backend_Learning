const fs = require('fs')

fs.readFile('salam.js', 'utf-8', (err, data) => {
    if(err){
        console.log("Error Code:", err.code)
        console.log("Message: ", err.message)
        return
    }
    console.log('Data: ', data)
})