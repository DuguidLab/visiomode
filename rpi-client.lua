local socket = require("socket")
local exports = {}

local reconnect = false 


-- Request parsers
local function parseTaskSettings(request)

end


local function parseSessionSettings(request)

end



-- RPi connection stuff
local function rpiCheck(ip, port)
    -- check if connection to ip and port is possible
    local client = socket.connect(ip, tonumber(port))
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
    end

    return client
end


local function rpiLoop(client, ip, port)
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
                rpiConnect(ip, port)
                data, err = client:receive()
                if data then 
                    allData[#allData+1] = data
                end
            end
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

exports.rpiCheck = rpiCheck
exports.rpiConnect = rpiConnect
exports.rpiLoop = rpiLoop

return exports

