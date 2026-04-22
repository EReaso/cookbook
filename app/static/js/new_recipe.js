function slugify(value) {
    return (value || "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/_+/g, "_")
        .replace(/^_+|_+$/g, "")
}

document.querySelector("#title").addEventListener("input", (e) => {
    document.querySelector("#slug").value = slugify(e.target.value)
})

function create_ingredient(doFocus = true) {
    const template = document.querySelector("#ingredient-template")
    let clone = template.cloneNode(true)

    clone.classList.remove("d-none")
    clone.setAttribute("id", "")
    clone.setAttribute("data-ingredient", Math.random().toString(36).substring(2, 15)) // Generate a random string as a temporary UUID for the ingredient
    clone.querySelectorAll("input[data-name]").forEach((input) => {
        input.setAttribute("name", input.getAttribute("data-name"))
    })

    document.querySelector("#ingredients").insertBefore(clone, template)

    clone.addEventListener("input", generate_ingredient_options)


    if (doFocus) clone.querySelector("input").focus()


    // Add hook for delete button
    clone.querySelector(".delete-parent").addEventListener("click", (e) => delete_ingredient(e.target.closest("li")))

    // Ensure the UI/select updates after adding a new row
    generate_ingredient_options()
    register_datalist_event_listeners()

    return clone
}

create_ingredient(false)

function delete_ingredient(row) {
    const uuid = row.getAttribute("data-ingredient")
    row.remove()

    // remove any matching option in the select (if present)
    const option = document.querySelector(`#ingredient-select option[data-ingredient="${uuid}"]`)
    if (option) option.remove()

    if (document.querySelectorAll("#ingredients li.ingredient-row:not(.d-none)").length === 0) {
        document.querySelector("#ingredient-select").innerHTML = "<option>Add an Ingredient to Insert</option>"
        document.querySelector("#ingredient-select").disabled = true
        document.querySelectorAll("#insert-ingredient-container button").forEach(btn => btn.disabled = true)
    }

    // keep options consistent after deletion
    generate_ingredient_options()
}

// Add more ingredient rows when the bottom row is selected
document.querySelectorAll("#create-ingredient-button").forEach(i => i.addEventListener("click", create_ingredient))

document.querySelector("#direction-editor-fullscreen").addEventListener("click", () => {
    document.fullscreenElement ? document.exitFullscreen() : document.querySelector("#direction-editor-card").requestFullscreen()
})

const easyMDE = new EasyMDE({uploadImage: false, inputStyle: "contenteditable"})
const cm = easyMDE.codemirror

document.querySelectorAll("#insert-ingredient-container button[data-js-template]").forEach(btn => btn.addEventListener("click", () => {
    const select = document.querySelector("#ingredient-select")
    const selectedOption = select?.selectedOptions?.[0]
    const ingredient = selectedOption?.value || ""
    // TODO: make this use the slug instead of name
    cm.replaceSelection(`:: ${btn.getAttribute("data-js-template").replace("ingredient", ingredient)} ::`)
}))

function generate_ingredient_options() {
    const ingredients = Array.from(document.querySelectorAll("#ingredients li"))
        .filter(i => !i.classList.contains("d-none") && i.querySelector('span input[name="name"]') && i.querySelector('span input[name="name"]').value.trim() !== "")
    const options = document.querySelector("#ingredient-select")
    options.innerHTML = ""

    if (ingredients.length > 0) {
        options.disabled = false
        document.querySelectorAll("#insert-ingredient-container button").forEach(btn => btn.disabled = false)
    } else {
        options.disabled = true
        document.querySelectorAll("#insert-ingredient-container button").forEach(btn => btn.disabled = true)
        options.innerHTML = "<option>Add an Ingredient to Insert</option>"
    }

    for (let i of ingredients) {
        const ingredient_name = i.querySelector('span input[name="name"]').value
        const option = options.appendChild(new Option(ingredient_name, ingredient_name))
        option.setAttribute("data-ingredient", i.getAttribute("data-ingredient"))
    }
}

document.querySelector("#submit").addEventListener("click", submit)

const INGREDIENT_FIELDS = ["amount", "unit", "name"]
const RECIPE_DRAFT_KEY = "new_recipe_draft_v1"
const DRAFT_SAVE_DEBOUNCE_MS = 300

let draftSaveTimer = null

function get_recipe_payload() {
    let data = Object.fromEntries(new FormData(document.querySelector("#recipe-metadata")))
    data["name"] = data["title"] || ""
    delete data["title"]

    // Disabled fields are omitted from FormData.
    data["slug"] = document.querySelector("#slug").value || ""
    data["directions"] = easyMDE.value()

    let raw_ingredient_data = new FormData(document.querySelector("#ingredient-form"))
    let arrs = INGREDIENT_FIELDS.map(i => raw_ingredient_data.getAll(i))

    data["recipe_ingredients"] = arrs[0].map((_, i) => {
        const ingredient = Object.fromEntries(INGREDIENT_FIELDS.map((k, v) => [k, arrs[v][i]]))
        ingredient.slug = slugify(ingredient.name)
        return ingredient
    }).filter((ingredient) => ingredient.name && ingredient.slug)

    return data
}

function save_recipe_draft() {
    localStorage.setItem(RECIPE_DRAFT_KEY, JSON.stringify(get_recipe_payload()))
}

function schedule_recipe_draft_save() {
    if (draftSaveTimer) clearTimeout(draftSaveTimer)
    draftSaveTimer = setTimeout(save_recipe_draft, DRAFT_SAVE_DEBOUNCE_MS)
}

function clear_recipe_draft() {
    localStorage.removeItem(RECIPE_DRAFT_KEY)
}

function restore_recipe_draft() {
    const raw = localStorage.getItem(RECIPE_DRAFT_KEY)
    if (!raw) return

    try {
        const payload = JSON.parse(raw)
        load_payload(payload)
    } catch {
        clear_recipe_draft()
    }
}

function submit() {
    const data = get_recipe_payload()

    console.log(data)
    fetch("", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    }).then((r) => {
        if (r.ok) clear_recipe_draft()
        alert(r.status)
    })
}

function load_payload(payload) {
    document.querySelectorAll("#ingredients li.ingredient-row:not(#ingredient-template)").forEach((node) => node.remove())

    document.querySelector("#title").value = payload.name || ""
    document.querySelector("#slug").value = payload.slug || ""
    document.querySelector("#cook_time").value = payload.cook_time || ""
    document.querySelector("#cook_temp").value = payload.cook_temp || ""
    document.querySelector("#prep_time").value = payload.prep_time || ""
    document.querySelector("#servings").value = payload.servings || ""

    easyMDE.value(payload.directions || "")

    if ((payload.recipe_ingredients || []).length > 0) {
        for (let i of payload.recipe_ingredients) {
            const Elem = create_ingredient(false)
            for (let key of INGREDIENT_FIELDS) {
                Elem.querySelector(`span input[name="${key}"]`).value = i[key] || ""
            }
        }
    } else {
        create_ingredient(false)
    }

    generate_ingredient_options()
}

document.querySelector("#recipe-metadata").addEventListener("input", schedule_recipe_draft_save)
document.querySelector("#ingredient-form").addEventListener("input", schedule_recipe_draft_save)
easyMDE.codemirror.on("change", schedule_recipe_draft_save)

restore_recipe_draft()
