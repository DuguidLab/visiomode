local composer = require("composer")
local saveload = require("saveload")

local scene = composer.newScene()

local settingsFile = "settings.json"

local controllerAddress, controllerPort  -- vars to hold user input

local function gotoMenu()
    composer.gotoScene("menu")
end

local function saveSettings()
    local settings = {
        address = controllerAddress.text,
        port = controllerPort.text
    }
    saveload.saveTable(settings, settingsFile)
    gotoMenu()
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create(event)

    -- Get existing settings or use defaults
    local settings = saveload.loadTable(settingsFile)
    if not settings then
        settings = {
            address = "0.0.0.0",
            port = "5000",
        }
    end

    -- Interface setup
    local sceneGroup = self.view

    local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
    background.x = display.contentCenterX
    background.y = display.contentCenterY

    local title = display.newText(sceneGroup, "Settings", display.contentCenterX, 70, native.SystemFont, 50)

    local ipTitle = display.newText(sceneGroup, "Controller IP: ", display.contentCenterX - 200, 300, native.SystemFont, 40)
    ipTitle.anchorX = 1

    controllerAddress = native.newTextField(display.contentCenterX + 200, 300, 300, 35)
    controllerAddress.text = settings.address
    sceneGroup:insert(controllerAddress)

    local portTitle = display.newText(sceneGroup, "Controller Port: ", display.contentCenterX - 200, 375, native.SystemFont, 40)
    portTitle.anchorX = 1

    controllerPort = native.newTextField(display.contentCenterX + 200, 375, 100, 35)
    controllerPort.text = settings.port
    sceneGroup:insert(controllerPort)

    local setupSessionButton = display.newText(sceneGroup, "Save Settings", display.contentCenterX - 200, 700, native.SystemFont, 45)
    setupSessionButton:addEventListener("tap", saveSettings)

    local goBackButton = display.newText(sceneGroup, "Go Back", display.contentCenterX + 200, 700, native.SystemFont, 45)
    goBackButton:addEventListener("tap", gotoMenu)
end


-- show()
function scene:show(event)

    local sceneGroup = self.view
    local phase = event.phase

    if (phase == "will") then
        -- publish taskSettings table
    elseif (phase == "did") then
        -- Code here runs when the scene is entirely on screen

    end
end


-- hide()
function scene:hide(event)

    local sceneGroup = self.view
    local phase = event.phase

    if (phase == "will") then

    elseif (phase == "did") then
        composer.removeScene("settings")
    end
end


-- destroy()
function scene:destroy(event)

    local sceneGroup = self.view
    -- Code here runs prior to the removal of scene's view

end


-- -----------------------------------------------------------------------------------
-- Scene event function listeners
-- -----------------------------------------------------------------------------------
scene:addEventListener("create", scene)
scene:addEventListener("show", scene)
scene:addEventListener("hide", scene)
scene:addEventListener("destroy", scene)
-- -----------------------------------------------------------------------------------

return scene
