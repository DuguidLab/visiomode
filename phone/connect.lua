
local composer = require( "composer" )
local saveload = require("saveload")

local scene = composer.newScene()

local settingsFile = "settings.json"


local rpiClient = require("rpi-client")
local widget = require( "widget" )
local controllerAddress
local controllerPort

local connectButton
local connectionMessage


local function connectionWrapper()
    connectButton.alpha = 0
    client = rpiClient.rpiConnect(controllerAddress.text, controllerPort.text)
    if client then
        print("Can connect!")
        connectionMessage.text = "Successfully connected to RPi Server"
        rpiClient.rpiLoop(client, controllerAddress.text, controllerPort.text)
    else
        print("Cannot connect to " .. controllerAddress.text)
        connectionMessage.text = "Could not connect to " .. controllerAddress.text .. " on port " .. controllerPort.text
        connectButton.alpha = 1
    end
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )
    -- Get existing settings or use defaults
    local settings = saveload.loadTable(settingsFile)
    if not settings then
        settings = {
            address = "0.0.0.0",
            port = "5000",
        }
    end

	local sceneGroup = self.view
	-- Code here runs when the scene is first created but has not yet appeared on screen

    local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
    background.x = display.contentCenterX
    background.y = display.contentCenterY

    local title = display.newText(sceneGroup, "Connect to Raspberry Pi Controller", display.contentCenterX, 70, native.SystemFont, 50)

    local subtitle = display.newText(sceneGroup, "Make sure that phone and controller are connected to the same network", display.contentCenterX, 150, native.SystemFont, 42)

    local ipTitle = display.newText(sceneGroup, "Controller Address: ", display.contentCenterX-200, 300, native.SystemFont, 40)
    ipTitle.anchorX = 1

    controllerAddress = native.newTextField(display.contentCenterX+200, 300, 300, 35)
    controllerAddress.text = settings.address
    sceneGroup:insert(controllerAddress)

    local portTitle = display.newText(sceneGroup, "Controller Port: ", display.contentCenterX-200, 375, native.SystemFont, 40)
    portTitle.anchorX = 1

    controllerPort = native.newTextField(display.contentCenterX+200, 375, 100, 35)
    controllerPort.text = settings.port
    sceneGroup:insert(controllerPort)

    connectionMessage = display.newText(sceneGroup, "", display.contentCenterX, 550, native.SystemFont, 42)

    connectButton = display.newText(sceneGroup, "Connect", display.contentCenterX, 700, native.SystemFont, 45)
    connectButton:addEventListener("tap", connectionWrapper)
end


-- show()
function scene:show( event )

	local sceneGroup = self.view
	local phase = event.phase

	if ( phase == "will" ) then
		-- Code here runs when the scene is still off screen (but is about to come on screen)

	elseif ( phase == "did" ) then
		-- Code here runs when the scene is entirely on screen

	end
end


-- hide()
function scene:hide( event )

	local sceneGroup = self.view
	local phase = event.phase

	if ( phase == "will" ) then
		-- Code here runs when the scene is on screen (but is about to go off screen)

	elseif ( phase == "did" ) then
        composer.removeScene("connect")
	end
end


-- destroy()
function scene:destroy( event )

	local sceneGroup = self.view
	-- Code here runs prior to the removal of scene's view

end


-- -----------------------------------------------------------------------------------
-- Scene event function listeners
-- -----------------------------------------------------------------------------------
scene:addEventListener( "create", scene )
scene:addEventListener( "show", scene )
scene:addEventListener( "hide", scene )
scene:addEventListener( "destroy", scene )
-- -----------------------------------------------------------------------------------

return scene
