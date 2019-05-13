local composer = require("composer")
local json = require("json")

local scene = composer.newScene()

local docs = system.DocumentsDirectory

local function gotoMenu()
    composer.gotoScene("menu")
end

local function loadSettings()

end

local function saveSettings()

end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create(event)

    local sceneGroup = self.view

    local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
    background.x = display.contentCenterX
    background.y = display.contentCenterY

    local title = display.newText(sceneGroup, "Settings", display.contentCenterX, 70, native.SystemFont, 50)

    local ipTitle = display.newText(sceneGroup, "Controller IP: ", display.contentCenterX - 200, 300, native.SystemFont, 40)
    ipTitle.anchorX = 1

    rpiServer = native.newTextField(display.contentCenterX + 200, 300, 300, 35)
    rpiServer.text = "0.0.0.0"
    sceneGroup:insert(rpiServer)

    local portTitle = display.newText(sceneGroup, "Controller Port: ", display.contentCenterX - 200, 375, native.SystemFont, 40)
    portTitle.anchorX = 1

    rpiSocket = native.newTextField(display.contentCenterX + 200, 375, 100, 35)
    rpiSocket.text = "5000"
    sceneGroup:insert(rpiSocket)

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
