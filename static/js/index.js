// console.log(google)

window.onload = () => {
    const locateBtn = document.getElementById('locateBtn')
    const map = document.getElementById('map')
    if(locateBtn) {
        locateBtn.addEventListener('click', async (e) => {
            console.log('clicked')
            navigator.geolocation.getCurrentPosition(async (pos) => {
                let latitude = pos.coords.latitude
                let longitude = pos.coords.longitude
                let payload = {
                    'latitude': latitude,
                    'longitude': longitude
                }
                let res = await fetch('/nearby',{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                res = await res.text()
                map.innerHTML = `<img src="data:image/png;base64,${res}"/>`
                console.log('done')
            })
        })
    }
}

function validateDocRegForm() {
    const form = document.getElementsByName("docReg")[0]
    console.log(form)
    console.log(form["council"].value)
    console.log(form["reg_no"].value)
    
    // use service to decide whether the doctor is valid or not
    const isValid = true

    if (isValid) {
        form.submit()
    } else {
        alert("We could not find you by your registration number. Please make sure thar the details that you enter are correct and retry.")
    }
}