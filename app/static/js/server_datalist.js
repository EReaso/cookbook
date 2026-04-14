function register_datalist_event_listeners() {
    document.querySelectorAll(".server-datalist").forEach(element => {
        element.addEventListener("input", async () => {
            const list = document.getElementById(element.getAttribute("list"))

            const url = list.getAttribute("data-url")
            console.log(url || "No datalist url")
            if (!url) return

            const queryUrl = `${url}?q=${encodeURIComponent(element.value)}`
            let resp = await fetch(queryUrl)

            if (resp.ok) {
                const data = await resp.json()
                list.innerHTML = ""
                data.forEach((item) => list.appendChild(new Option(item.name, item.slug)))
            }
        })
    })
}

register_datalist_event_listeners()
