local exports = {}

local socket = require("socket")
local json = require("json")
local composer = require( "composer" )


local reconnect = false 


-- Request parsers
local function parseSettings(request)
    return json.decode(request)
end


-- RPi connection stuff
local function rpiCheck(ip, port)
    -- check if connection to ip and port is possible
    local client = socket.connect(ip, tonumber(port))
    client:settimeout(0)
    if client == nil then
        return false
    end
    client:send("hello")
    client:shutdown()
    return true
end


local function rpiConnect(ip, port)
    -- Connect to the client
    local client = socket.connect(ip, tonumber(port))
    if client == nil then
        return false
    end
    -- Get IP and port from client
    local _, lport = client:getsockname()
    client:settimeout(0)
    client:setoption( "tcp-nodelay", true ) 

    -- Print the IP address and port to the terminal
    print( "IP Address:", ip )
    print( "Port:", lport )

    if not reconnect then
        client:send("connect")
        reconnect = true
    else 
        -- TODO include session ID in restore request
        client:send("restore")
    end

    return client
end


local function rpiLoop(client, ip, port)
    local clientPulse
    composer.setVariable('buffer', {})

    local function cPulse()
        local allData = {}
        local data, err
        local buffer = composer.getVariable('buffer')

        repeat 
            data, err = client:receive()
            if data then
                allData[#allData+1] = data
            end
            if (err == "closed" and clientPulse) then
                print("reconnecting...")
                rpiConnect(ip, port)
                data, err = client:receive()
                if data then 
                    allData[#allData+1] = data
                end
            end
        until not data

        if ( #allData > 0 ) then 
            for i, thisData in ipairs(allData) do
                print("received: ", thisData)
                if string.match(thisData, "{*}") then  -- does it look like json?
                    settings = parseSettings(thisData)
                    composer.setVariable("taskSettings", settings.task)
                    composer.setVariable("sessionSettings", settings.session)
                    composer.gotoScene("task")
                end
            end
        end

        for i, msg in pairs(buffer) do
            print('sending: ' .. msg)
            local data, err = client:send(msg)
            if (err == "closed" and clientPulse) then  --try to reconnect and resend
                rpiConnect(ip, port)
                data, err = client:send(msg)
            end
            if not err then 
                composer.setVariable('buffer', {})
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

exports.rpiCheck = rpiCheck
exports.rpiConnect = rpiConnect
exports.rpiLoop = rpiLoop

return exports

