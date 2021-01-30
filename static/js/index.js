// console.log(google)

const locateBtn = document.getElementById('locateBtn')
const map = document.getElementById('map')
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
