
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------

local socket = require( "socket" )
local widget = require( "widget" )
local rpiServer
local rpiSocket


local function connectRpi()
    print(rpiServer.text)
    -- Connect to the client
    local client = socket.connect(rpiServer.text, tonumber(rpiSocket.text) )
    if client == nil then
        return false
    end
    -- Get IP and port from client
    local ip, port = client:getsockname()
    client:settimeout(0)
    client:setoption( "tcp-nodelay", true ) 

    -- Print the IP address and port to the terminal
    print( "IP Address:", ip )
    print( "Port:", port )
    client:send("connected")

    return client
end


local function rpiLoop(client)
    local buffer = {}
    local clientPulse

    local function cPulse()
        local allData = {}
        local data, err

        repeat 
            data, err = client:receive()
            if data then
                allData[#allData+1] = data
            end
            if (err == "closed" and clientPulse) then
                print("reconnecting...")
                connectRpi()
                data, err = client:receive()
                if data then 
                    allData[#allData+1] = data
                end
            end
            print(data)
        until not data

        if ( #allData > 0 ) then 
            for i, thisData in ipairs(allData) do
                print("thisData: ", thisData)
            end
        end
    end

    clientPulse = timer.performWithDelay(100, cPulse, 0)

    local function stopClient()
        timer.cancel(clientPulse)
        clientPulse = nil
        client:close()
    end

    return stopClient
end


local function connectionWrapper()
    client = connectRpi()
    rpiLoop(client)
end


-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )

	local sceneGroup = self.view
	-- Code here runs when the scene is first created but has not yet appeared on screen

    local background = display.newImageRect(sceneGroup, "assets/menu-background.jpg", 1400, 800)
    background.x = display.contentCenterX
    background.y = display.contentCenterY

    local title = display.newText(sceneGroup, "Connect to Raspberry Pi Controller", display.contentCenterX, 70, native.SystemFont, 50)

    local subtitle = display.newText(sceneGroup, "Make sure that phone and RPi are connected to the same network", display.contentCenterX, 150, native.SystemFont, 42)

    local ipTitle = display.newText(sceneGroup, "RPi IP: ", display.contentCenterX-200, 300, native.SystemFont, 40)
    ipTitle.anchorX = 1

    rpiServer = native.newTextField(display.contentCenterX+200, 300, 300, 35)
    sceneGroup:insert(rpiServer)

    local portTitle = display.newText(sceneGroup, "RPi Port: ", display.contentCenterX-200, 375, native.SystemFont, 40)
    portTitle.anchorX = 1

    rpiSocket = native.newTextField(display.contentCenterX+200, 375, 100, 35)
    sceneGroup:insert(rpiSocket)

    local connectButton = display.newText(sceneGroup, "Connect", display.contentCenterX, 700, native.SystemFont, 45)
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
		-- Code here runs immediately after the scene goes entirely off screen

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
