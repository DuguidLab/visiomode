-- Module to save and load files to or from phone memory
local M = {}

local json = require("json")
local defaultLocation = system.DocumentsDirectory

function M.loadTable(filename, location)
    local loc = location
    if not location then
        loc = defaultLocation
    end

    local path = system.pathForFile(filename, loc)
    local file, errorString = io.open(path, "r")

    if not file then
        print("File Error: " .. errorString)
        return false
    end

    local contents = file:read("*a")  -- read as raw file string
    local table = json.decode(contents)  -- parse raw to json

    io.close(file)

    return table
end

function M.saveTable(table, filename, location)
    local loc = location
    if not location then
        loc = defaultLocation
    end

    local path = system.pathForFile(filename, loc)
    local file, errorString = io.open(path, "w")

    if not file then
        print("File error: " .. errorString)
        return false
    end

    file:write(json.encode(table))  -- write encoded lua table as json
    io.close(file)

    return true
end

return M