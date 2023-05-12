/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let table = document.getElementById("animalsTableData");
let editAnimalButton = document.getElementById('edit-animal-btn');
let animals = [];


function loadAnimals() {
    fetch("/api/animals")
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            animals = data.animals;
            animals.sort((b, a) => new Date(a.date_of_birth).getDate() - new Date(b.date_of_birth).getDate());

            let animalsTableData = document.getElementById("animalsTableData");
            animalsTableData.innerHTML = "";
            animals.forEach(animal => {
                let row = animalsTableData.insertRow();
                let animal_id = row.insertCell(0);
                animal_id.innerHTML = animal.animal_id;
                let date_of_birth = row.insertCell(1);
                date_of_birth.innerHTML = animal.date_of_birth;
                let sex = row.insertCell(2);
                sex.innerHTML = animal.sex;
                let description = row.insertCell(3);
                description.innerHTML = animal.description;
            });
        });
}

table.onclick = function (event) {
    let animal_id = event.target.parentNode.cells[0].innerHTML;
    let selected_animal = animals.find(element => element.animal_id == animal_id);
    console.log(selected_animal);
    $("#editAnimal").modal();
    document.getElementById("animal-id").value = selected_animal.animal_id;
    document.getElementById("animal-dob").value = selected_animal.date_of_birth;
    document.getElementById("animal-sex").value = selected_animal.sex;
    document.getElementById("animal-species").value = selected_animal.species;
    document.getElementById("animal-genotype").value = selected_animal.genotype;
    document.getElementById("animal-description").value = selected_animal.description;
}

function editAnimal() {
    let animalId = document.getElementById("animal-id").value;
    let animalDob = document.getElementById("animal-dob").value;
    let animalSex = document.getElementById("animal-sex").value;
    let animalSpecies = document.getElementById("animal-species").value;
    let animalGenotype = document.getElementById("animal-genotype").value;
    let animalDescription = document.getElementById("animal-description").value;

    $.ajax({
        type: 'POST',
        url: "/api/animals",
        data: JSON.stringify({
            type: "edit",
            data: {
                id: animalId,
                dob: animalDob,
                sex: animalSex,
                species: animalSpecies,
                genotype: animalGenotype,
                description: animalDescription,
            },
        }),
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            loadAnimals();
            $("#editAnimal").modal("toggle")
        }
    });
}

editAnimalButton.onclick = function () {
    editAnimal();
}

loadAnimals();
