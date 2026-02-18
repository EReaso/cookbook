const inputs = [["Slug", "slug", "text"], ["Cook Time (minutes)", "cook_time", "number"], ["Cook Temp", "cook_temp", "number"], ["Prep Time (minutes)", "prep_time", "number"], ["Servings", "servings", "number"]]

for (let i of inputs) {
    let input = document.querySelector(".input_row").cloneNode(true)
    input.querySelector("label").innerText = i[0]
    input.querySelector("input").setAttribute("name", i[1])
    input.querySelector("input").setAttribute("id", i[1])
    input.querySelector("input").setAttribute("type", i[2])
    input.querySelector("label").setAttribute("for", i[1])
    document.querySelector(".input_container").appendChild(input)
}

// Disable slug input and auto-update on title change
document.querySelector("#slug").setAttribute("disabled", "true")
document.querySelector("#title").addEventListener("input", (e) => {
    document.querySelector("#slug").value = e.target.value.toLowerCase().replace(/[^_a-z0-9]/g, "_")
})

function create_ingredient() {
    const template = document.querySelector("#ingredient_template")
    let clone = template.cloneNode(true)

    clone.classList.remove("d-none")
    clone.setAttribute("id", "")
    clone.setAttribute("data-ingredient", crypto.randomUUID())
    document.querySelector("#ingredient-select").appendChild(clone)

    document.querySelector("#ingredients").insertBefore(clone, template)

    clone.addEventListener("input", generate_ingredient_options)

    clone.querySelector("input").focus()


    // Add hook for delete button
    clone.querySelector(".delete-parent").addEventListener("click", (e) => delete_ingredient(e.target.closest(".ingredient_row")))
}

create_ingredient()

function delete_ingredient(row) {
    const uuid = row.getAttribute("data-ingredient")
    row.remove()
    document.querySelector(`[data-ingredient="${uuid}"]`).remove()
    if (document.querySelectorAll("#ingredients li:not(#ingredient_template)").length === 0) {
        document.querySelector("#ingredient-select").innerHTML = "<option>Add an Ingredient to Insert</option>"
        document.querySelectorAll("#insert-ingredient-container button").forEach(btn => btn.disabled = true)
    }
}

// Add more ingredient rows when the bottom row is selected
document.querySelectorAll("#create-ingredient-button").forEach(i => i.addEventListener("click", create_ingredient))

document.querySelector("#direction-editor-fullscreen").addEventListener("click", () => {
    document.fullscreenElement ? document.exitFullscreen() : document.querySelector("#direction-editor-card").requestFullscreen()
})

const easyMDE = new EasyMDE({uploadImage: true, inputStyle: "contenteditable"})
const cm = easyMDE.codemirror

document.querySelectorAll("#insert-ingredient-container button[data-js-template]").forEach(btn =>
    btn.addEventListener("click", () => {
        const select = document.querySelector("#ingredient-select")
        const selectedOption = select?.selectedOptions?.[0]
        const ingredientRow = selectedOption
            ? document.querySelector(`[data-ingredient="${selectedOption.getAttribute("data-ingredient")}"]`)
            : null
        const ingredient = selectedOption?.value || ""
        cm.replaceSelection(`:: ${btn.getAttribute("data-js-template").replace("ingredient", ingredient)} ::`)
    })
)

function generate_ingredient_options() {
    const ingredients = document.querySelectorAll("#ingredients li:has(span>input[value])")
    const options = document.querySelector("#ingredient-select")
    options.innerHTML = ""

    if (ingredients.length !== 0) {
        document.querySelectorAll("#insert-ingredient-container button").forEach(btn => btn.disabled = false)
    }

    for (let i of ingredients) {
        const ingredient_slug = i.querySelector('span input[name="ingredient_slug"]').value
        const option = options.appendChild(new Option(ingredient_slug, ingredient_slug))
        option.setAttribute("data-ingredient", i.getAttribute("data-ingredient"))
    }
}