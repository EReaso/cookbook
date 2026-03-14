function register_datalist_event_listeners() {
    document.querySelectorAll(".server-datalist").forEach(element => {
        element.addEventListener("input", async () => {
            const list = document.getElementById(element.getAttribute("list"))

            const url = list.getAttribute("data-url")

            if (!url) return

            let resp = await fetch(url, {data: {query: this.value}})

            if (resp.ok) {
                const data = await resp.json()
                list.innerHTML = ""
                let nodes = data.map((item) => list.appendChild(new Option(item.name, item.value)))
            }
        })
    })
}

register_datalist_event_listeners()
