const inputs = [
    // Label, name/id, type
    ["Slug", "slug", "text"],
    ["Cook Time (minutes)", "cook_time", "number"],
    ["Cook Temp", "cook_temp", "number"],
    ["Prep Time (minutes)", "prep_time", "number"],
    ["Servings", "servings", "number"]
]

for (let i of inputs) {
    let input = document.querySelector(".input-row").cloneNode(true)
    input.querySelector("label").innerText = i[0]
    input.querySelector("input").setAttribute("name", i[1])
    input.querySelector("input").setAttribute("id", i[1])
    input.querySelector("input").setAttribute("type", i[2])
    input.querySelector("label").setAttribute("for", i[1])
    document.querySelector(".input-container").appendChild(input)
}

// Disable slug input and auto-update on title change
document.querySelector("#slug").disabled = true
document.querySelector("#title").addEventListener("input", (e) => {
    document.querySelector("#slug").value = e.target.value.toLowerCase().replace(/[^_a-z0-9]/g, "_")
})

function create_ingredient(doFocus = true) {
    const template = document.querySelector("#ingredient-template")
    let clone = template.cloneNode(true)

    clone.classList.remove("d-none")
    clone.setAttribute("id", "")
    clone.setAttribute("data-ingredient", Math.random().toString(36).substring(2, 15)) // Generate a random string as a temporary UUID for the ingredient

    document.querySelector("#ingredients").insertBefore(clone, template)

    clone.addEventListener("input", generate_ingredient_options)


    if (doFocus) clone.querySelector("input").focus()


    // Add hook for delete button
    clone.querySelector(".delete-parent").addEventListener("click", (e) => delete_ingredient(e.target.closest(".ingredient_row")))

    // Ensure the UI/select updates after adding a new row
    generate_ingredient_options()
}

create_ingredient(false)

function delete_ingredient(row) {
    const uuid = row.getAttribute("data-ingredient")
    row.remove()

    // remove any matching option in the select (if present)
    const option = document.querySelector(`#ingredient-select option[data-ingredient="${uuid}"]`)
    if (option) option.remove()

    if (document.querySelectorAll("#ingredients li:not(#ingredient-template)").length === 0) {
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
    const ingredientRow = selectedOption ? document.querySelector(`[data-ingredient="${selectedOption.getAttribute("data-ingredient")}"]`) : null
    const ingredient = selectedOption?.value || ""
    cm.replaceSelection(`:: ${btn.getAttribute("data-js-template").replace("ingredient", ingredient)} ::`)
}))

function generate_ingredient_options() {
    const ingredients = Array.from(document.querySelectorAll("#ingredients li"))
        .filter(i => !i.classList.contains("d-none") && i.querySelector('span input[name="ingredient_slug"]') && i.querySelector('span input[name="ingredient_slug"]').value.trim() !== "")
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
        const ingredient_slug = i.querySelector('span input[name="ingredient-slug"]').value
        const option = options.appendChild(new Option(ingredient_slug, ingredient_slug))
        option.setAttribute("data-ingredient", i.getAttribute("data-ingredient"))
    }
}

document.querySelector("#submit").addEventListener("click", submit)

function submit() {
    // Source - https://stackoverflow.com/a/10284006
    // Posted by ninjagecko, modified by community. See post 'Timeline' for change history
    // Retrieved 2026-02-20, License - CC BY-SA 4.0

    const zip = rows => rows[0].map((_, c) => rows.map(row => row[c]))


    let data = document.querySelector("#recipe-metadata").formData()
    data.directions = document.querySelector("#direction-editor").value

    let raw_ingredient_data = document.querySelector("#ingredients").formData()
    console.log(raw_ingredient_data)


}