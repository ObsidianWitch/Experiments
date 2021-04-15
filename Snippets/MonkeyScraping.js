// ==UserScript==
// @name Scrape webtoon
// @match *://www.webtoons.com/*/viewer*#monkey
// ==/UserScript==

// Example: https://www.webtoons.com/en/supernatural/muted/episode-1/viewer?title_no=1566&episode_no=1#monkey

window.ulocation = new URL(window.location)
let epi = ulocation.searchParams.get('episode_no')
epi = epi.toString().padStart(3, '0')

let promises = []
document.querySelectorAll('#_imageList img').forEach((img, imgi) => {
    let p = fetch(img.src)
        .then(response => response.blob())
        .then(blob => {
            let a = document.createElement('a')
            a.href = URL.createObjectURL(blob)
            imgi = imgi.toString().padStart(3, '0')
            let path = new URL(img.src).pathname
            path = path.substring(path.lastIndexOf('/') + 1)
            a.download = `${epi}_${imgi}_${path}`
            a.click()
        })
    promises.push(p)
})

Promise.all(promises)
    .then(_ => window.location = document.querySelector('a.pg_next').href + '#monkey')
